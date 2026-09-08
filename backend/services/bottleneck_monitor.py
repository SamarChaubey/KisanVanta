import asyncio
import logging
import os
from datetime import datetime, timezone

from database import get_collection
from services.centre_status_service import recompute_centre_status

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


def monitor_centres():
    centres = get_collection('procurement_centres').find({'status': 'open'})
    notifications = get_collection('notifications')
    now = datetime.now(timezone.utc)

    for centre in centres:
        recompute_centre_status(centre['_id'])
        status = get_collection('centre_status').find_one({'centreId': centre['_id']}) or {}
        bottlenecks = _bottlenecks_for_centre(centre, status)
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