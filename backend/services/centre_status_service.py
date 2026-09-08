from datetime import datetime, timezone
from database import get_collection

ACTIVE_STATUSES = {'waiting', 'assaying', 'weighing'}


def recompute_centre_status(centre_id):
    centre = get_collection('procurement_centres').find_one({'_id': centre_id})
    if not centre:
        return

    farmers_waiting = get_collection('procurement_records').count_documents({
        'centreId': centre_id,
        'status': {'$in': list(ACTIVE_STATUSES)},
    })

    get_collection('centre_status').update_one(
        {'centreId': centre_id},
        {'$set': {
            'centreId': centre_id,
            'farmersWaiting': farmers_waiting,
            'processingRate': centre['processingRate'],
            'storageUsed': centre['currentStorage'],
            'storageCapacity': centre['storageCapacity'],
            'liftingRate': centre['liftingCapacity'],
            'updatedAt': datetime.now(timezone.utc),
        }},
        upsert=True,
    )