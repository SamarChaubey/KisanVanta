import asyncio
import logging
import os
from datetime import datetime, timezone

from database import get_collection
from services.centre_status_service import recompute_centre_status
from services.risk_assessor import assess_risk_with_llm

logger = logging.getLogger(__name__)

MONITOR_INTERVAL_SECONDS = int(os.getenv('BOTTLENECK_MONITOR_INTERVAL_SECONDS', '60'))
QUEUE_HOURS_THRESHOLD = float(os.getenv('BOTTLENECK_QUEUE_HOURS_THRESHOLD', '2'))
STORAGE_UTILIZATION_THRESHOLD = float(
    os.getenv('BOTTLENECK_STORAGE_UTILIZATION_THRESHOLD', '0.8'),
)


def _bottlenecks_for_centre(centre, status):
    bottlenecks = []
    processing_rate = status.get('processingRate', 0)
    farmers_waiting = status.get('farmersWaiting', 0)
    storage_capacity = status.get('storageCapacity', 0)
    storage_used = status.get('storageUsed', 0)
    lifting_rate = status.get('liftingRate', 0)

    if processing_rate > 0 and farmers_waiting / processing_rate >= QUEUE_HOURS_THRESHOLD:
        bottlenecks.append({
            'type': 'queue_delay',
            'severity': 'high' if farmers_waiting / processing_rate >= 4 else 'medium',
            'message': (
                f"Queue is estimated at {farmers_waiting / processing_rate:.1f} hours "
                f"for {centre['name']}."
            ),
        })

    if storage_capacity > 0 and storage_used / storage_capacity >= STORAGE_UTILIZATION_THRESHOLD:
        utilization = storage_used / storage_capacity * 100
        bottlenecks.append({
            'type': 'storage_capacity',
            'severity': 'high' if utilization >= 90 else 'medium',
            'message': f"Storage is {utilization:.0f}% full at {centre['name']}.",
        })

    if lifting_rate > 0 and processing_rate > lifting_rate:
        bottlenecks.append({
            'type': 'lifting_backlog',
            'severity': 'medium',
            'message': (
                f"Processing rate ({processing_rate}) exceeds lifting rate "
                f"({lifting_rate}) at {centre['name']}."
            ),
        })

    return bottlenecks


def risk_assessment(centre, status):
    processing_rate = status.get('processingRate', 0)
    farmers_waiting = status.get('farmersWaiting', 0)
    storage_capacity = status.get('storageCapacity', 0)
    storage_used = status.get('storageUsed', 0)
    lifting_rate = status.get('liftingRate', 0)
    queue_hours = farmers_waiting / processing_rate if processing_rate else None
    storage_utilization = storage_used / storage_capacity if storage_capacity else None
    lifting_gap = max(processing_rate - lifting_rate, 0)

    score = 0
    if queue_hours is not None:
        score += min(queue_hours / 6, 1) * 45
    if storage_utilization is not None:
        score += min(storage_utilization, 1) * 35
    if processing_rate:
        score += min(lifting_gap / processing_rate, 1) * 20
    score = round(min(score, 100), 1)

    return {
        'riskScore': score,
        'riskLevel': 'high' if score >= 70 else 'medium' if score >= 35 else 'low',
        'queueHours': round(queue_hours, 2) if queue_hours is not None else None,
        'storageUtilization': round(storage_utilization * 100, 1)
        if storage_utilization is not None else None,
        'liftingGap': lifting_gap,
        'bottleneckTypes': [item['type'] for item in _bottlenecks_for_centre(centre, status)],
    }


def _request_counts(centre_id):
    counts = {}
    for status in ('received', 'alternative_suggested', 'unavailable', 'confirmed', 'closed', 'completed'):
        counts[status] = get_collection('slot_requests').count_documents({
            'centreId': centre_id,
            'status': status,
        })
    return counts


def monitor_centres():
    centres = get_collection('procurement_centres').find({'status': 'open'})
    notifications = get_collection('notifications')
    now = datetime.now(timezone.utc)

    for centre in centres:
        recompute_centre_status(centre['_id'])
        status = get_collection('centre_status').find_one({'centreId': centre['_id']}) or {}
        bottlenecks = _bottlenecks_for_centre(centre, status)
        available_slots = list(get_collection('booking_slots').find({
            'centreId': centre['_id'],
            'status': 'available',
            '$expr': {'$lt': ['$booked', '$capacity']},
        }).limit(20))
        recent_history = list(get_collection('risk_snapshots').find(
            {'centreId': centre['_id']},
            {
                'riskScore': 1,
                'queueHours': 1,
                'storageUtilization': 1,
                'createdAt': 1,
            },
        ).sort('createdAt', -1).limit(12))
        assessment = assess_risk_with_llm(
            centre,
            status,
            available_slots,
            _request_counts(centre['_id']),
            bottlenecks,
            recent_history,
        )
        snapshots = get_collection('risk_snapshots')
        snapshots.insert_one({
            'centreId': centre['_id'],
            'centreName': centre['name'],
            **assessment,
            'createdAt': now,
        })
        active_types = {item['type'] for item in bottlenecks}

        notifications.update_many(
            {
                'centreId': centre['_id'],
                'recipientRole': 'procurement_officer',
                'active': True,
                'type': {'$nin': list(active_types)},
            },
            {'$set': {'active': False, 'resolvedAt': now}},
        )

        for bottleneck in bottlenecks:
            notifications.update_one(
                {
                    'centreId': centre['_id'],
                    'recipientRole': 'procurement_officer',
                    'type': bottleneck['type'],
                    'active': True,
                },
                {
                    '$set': {
                        'severity': bottleneck['severity'],
                        'message': bottleneck['message'],
                        'updatedAt': now,
                    },
                    '$setOnInsert': {
                        'centreName': centre['name'],
                        'read': False,
                        'active': True,
                        'createdAt': now,
                    },
                },
                upsert=True,
            )


async def run_bottleneck_monitor(stop_event):
    while not stop_event.is_set():
        try:
            await asyncio.to_thread(monitor_centres)
        except Exception:
            logger.exception('Bottleneck monitor cycle failed')

        try:
            await asyncio.wait_for(stop_event.wait(), timeout=MONITOR_INTERVAL_SECONDS)
        except asyncio.TimeoutError:
            continue