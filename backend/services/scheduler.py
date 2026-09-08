from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId

from database import get_collection

from services.booking_service import BookingSystemError, book_slot


def _minutes(time_value):
    for time_format in ('%H:%M', '%I:%M %p'):
        try:
            return datetime.strptime(time_value, time_format).hour * 60 + datetime.strptime(
                time_value,
                time_format,
            ).minute
        except ValueError:
            continue
    raise ValueError('Time must use HH:MM or h:mm AM/PM format')


def _object_id(value, field_name):
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        raise ValueError(f'Invalid {field_name}') from None


def _available_slots(centre_id, date):
    return list(get_collection('booking_slots').find({
        'centreId': centre_id,
        'date': date,
        'status': 'available',
        '$expr': {'$lt': ['$booked', '$capacity']},
    }))


def schedule_slot(request, request_id):
    centre_id = _object_id(request['centreId'], 'centreId')
    farmer_id = _object_id(request['farmerId'], 'farmerId')
    centres = get_collection('procurement_centres')
    centre = centres.find_one({'_id': centre_id, 'status': 'open'})
    if not centre:
        raise ValueError('Centre not found or not open')
    if request['crop'] not in centre.get('crops', []):
        raise ValueError('Crop is not accepted at the requested centre')
    farmer = get_collection('users').find_one({'_id': farmer_id, 'role': 'farmer'})
    if not farmer:
        raise ValueError('Farmer not found')
    if farmer.get('centreId') and farmer['centreId'] != centre_id:
        raise ValueError('Farmer is not linked to the requested centre')

    requested_time = request['preferredTime']
    available_slots = _available_slots(centre_id, request['requestedDate'])
    exact_slot = next(
        (slot for slot in available_slots
         if _minutes(slot['time']) == _minutes(requested_time)),
        None,
    )

    if exact_slot:
        try:
            booking = book_slot(exact_slot, request['farmerId'])
        except BookingSystemError as error:
            return {'status': 'booking_failed', 'message': str(error)}
        if booking.get('status') != 'confirmed':
            return {
                'status': 'booking_failed',
                'message': 'The booking system did not confirm the requested slot.',
            }
        _confirm_request(request_id, request, exact_slot)
        return {'status': 'confirmed', 'slot': booking.get('slot', exact_slot)}

    if not available_slots:
        return {
            'status': 'unavailable',
            'message': 'No suitable procurement slots are available.',
        }

    suggested_slot = min(
        available_slots,
        key=lambda slot: abs(_minutes(slot['time']) - _minutes(requested_time)),
    )
    get_collection('slot_requests').update_one(
        {'_id': request_id},
        {'$set': {
            'status': 'alternative_suggested',
            'suggestedSlot': {
                'date': suggested_slot['date'],
                'time': suggested_slot['time'],
            },
        }},
    )
    return {
        'status': 'alternative_suggested',
        'message': 'The requested slot is unavailable. Please accept the suggested slot.',
        'suggestedSlot': {
            'date': suggested_slot['date'],
            'time': suggested_slot['time'],
        },
    }


def accept_alternative(request, suggested_slot):
    slot = get_collection('booking_slots').find_one({
        'centreId': _object_id(request['centreId'], 'centreId'),
        'date': suggested_slot['date'],
        'time': suggested_slot['time'],
        'status': 'available',
        '$expr': {'$lt': ['$booked', '$capacity']},
    })
    if not slot:
        return {'status': 'unavailable', 'message': 'Suggested slot is no longer available.'}
    try:
        booking = book_slot(slot, request['farmerId'])
    except BookingSystemError as error:
        return {
            'status': 'booking_failed',
            'message': str(error),
        }

    if booking.get('status') != 'confirmed':
        return {
            'status': 'booking_failed',
            'message': 'The booking system did not confirm the suggested slot.',
        }
    request_id = request['_id']
    _confirm_request(request_id, request, slot)
    return {'status': 'confirmed', 'slot': booking.get('slot', suggested_slot)}


def _confirm_request(request_id, request, slot):
    final_slot = {'date': slot['date'], 'time': slot['time']}
    get_collection('slot_requests').update_one(
        {'_id': request_id},
        {'$set': {
            'status': 'confirmed',
            'finalSlot': final_slot,
            'updatedAt': datetime.now(timezone.utc),
        }},
    )
