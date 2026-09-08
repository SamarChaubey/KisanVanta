from bson import ObjectId
from pymongo import ReturnDocument
from database import get_collection


class BookingSystemError(Exception):
    """Raised when a slot cannot be booked."""


def _serialize_mongo_values(value):
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, dict):
        return {key: _serialize_mongo_values(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_serialize_mongo_values(item) for item in value]
    return value


def book_slot(slot, farmer_id):
    """Atomically claim a slot. Prevents overbooking under concurrent requests."""
    result = get_collection('booking_slots').find_one_and_update(
        {
            '_id': slot['_id'],
            'status': 'available',
            '$expr': {'$lt': ['$booked', '$capacity']},
        },
        {'$inc': {'booked': 1}},
        return_document=ReturnDocument.AFTER,
    )
    if not result:
        raise BookingSystemError('Slot is no longer available')

    if result['booked'] >= result['capacity']:
        get_collection('booking_slots').update_one(
            {'_id': result['_id']},
            {'$set': {'status': 'full'}},
        )

    return {'status': 'confirmed', 'slot': _serialize_mongo_values(result)}