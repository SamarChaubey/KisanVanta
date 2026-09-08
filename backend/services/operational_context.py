import json

from bson import ObjectId

from database import get_collection
from services.bottleneck_monitor import _bottlenecks_for_centre


def _serialize(value):
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, dict):
        return {key: _serialize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    return value


def _centre_context(centre):
    centre_id = centre['_id']
    status = get_collection('centre_status').find_one({'centreId': centre_id}) or {}
    slots = list(get_collection('booking_slots').find({
        'centreId': centre_id,
        'status': 'available',
        '$expr': {'$lt': ['$booked', '$capacity']},
    }).sort([('date', 1), ('time', 1)]).limit(20))
    notifications = list(get_collection('notifications').find({
        'centreId': centre_id,
        'recipientRole': 'procurement_officer',
        'active': True,
    }))
    bottlenecks = _bottlenecks_for_centre(centre, status)

    return {
        'centre': _serialize(centre),
        'currentStatus': _serialize(status),
        'availableSlots': _serialize(slots),
        'activeBottlenecks': _serialize(bottlenecks),
        'activeNotifications': _serialize(notifications),
    }


def gather_operational_context(centre_id=None):
    query = {'_id': centre_id} if centre_id else {'status': 'open'}
    centres = list(get_collection('procurement_centres').find(query))
    context = [_centre_context(centre) for centre in centres]
    return json.dumps(context, default=str, indent=2)


def gather_farmer_operational_context(centre_ids):
    context = []
    for centre_id in centre_ids:
        centre = get_collection('procurement_centres').find_one({'_id': centre_id})
        if centre:
            context.append(_centre_context(centre))
    return json.dumps(context, default=str, indent=2)