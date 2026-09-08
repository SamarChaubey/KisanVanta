from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter
from fastapi import HTTPException
from pydantic import BaseModel

from database import get_collection
from services.booking_service import BookingSystemError
from services.scheduler import accept_alternative, confirm_slot_request, schedule_slot

router = APIRouter()


class SlotRequest(BaseModel):
    farmerId: str
    centreId: str
    crop: str
    quantity: float
    requestedDate: str
    preferredTime: str


class AlternativeAcceptance(BaseModel):
    date: str
    time: str


class OfficerConfirmation(BaseModel):
    date: str | None = None
    time: str | None = None


class OfficerClosure(BaseModel):
    reason: str = 'Closed by procurement officer'


def _object_id(value, field_name):
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        raise HTTPException(status_code=400, detail=f'Invalid {field_name}') from None


def _stringify(value):
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, dict):
        return {key: _stringify(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_stringify(item) for item in value]
    return value


@router.get('')
def list_slot_requests(centreId: str | None = None, status: str | None = None):
    query = {}
    if centreId:
        query['centreId'] = _object_id(centreId, 'centreId')
    if status:
        query['status'] = status
    requests = list(
        get_collection('slot_requests').find(query).sort('createdAt', -1),
    )
    return [_stringify(request) for request in requests]


@router.post('')
def create_slot_request(request: SlotRequest):
    request_data = request.model_dump()
    request_id = ObjectId()
    request_data['_id'] = request_id
    now = datetime.now(timezone.utc)
    get_collection('slot_requests').insert_one({
        '_id': request_id,
        'farmerId': _object_id(request.farmerId, 'farmerId'),
        'centreId': _object_id(request.centreId, 'centreId'),
        'crop': request.crop,
        'quantity': request.quantity,
        'requestedDate': request.requestedDate,
        'preferredTime': request.preferredTime,
        'requestedSlot': {
            'date': request.requestedDate,
            'time': request.preferredTime,
        },
        'status': 'received',
        'createdAt': now,
        'updatedAt': now,
    })

    try:
        result = schedule_slot(request_data, request_id)
    except BookingSystemError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except ValueError as error:
        get_collection('slot_requests').update_one(
            {'_id': request_id},
            {'$set': {'status': 'rejected', 'updatedAt': datetime.now(timezone.utc)}},
        )
        raise HTTPException(status_code=400, detail=str(error)) from error

    return {'requestId': str(request_id), **result}


@router.post('/{request_id}/accept-alternative')
def accept_slot_alternative(request_id: str, acceptance: AlternativeAcceptance):
    request_object_id = _object_id(request_id, 'requestId')
    stored_request = get_collection('slot_requests').find_one({'_id': request_object_id})
    if not stored_request:
        raise HTTPException(status_code=404, detail='Slot request not found')
    suggested_slot = stored_request.get('suggestedSlot')
    if not suggested_slot or suggested_slot != acceptance.model_dump():
        raise HTTPException(status_code=400, detail='Invalid suggested slot')

    stored_request['_id'] = request_object_id
    result = accept_alternative(stored_request, suggested_slot)
    return {'requestId': request_id, **result}


@router.post('/{request_id}/officer-confirm')
def officer_confirm_slot_request(
    request_id: str,
    confirmation: OfficerConfirmation,
):
    request_object_id = _object_id(request_id, 'requestId')
    stored_request = get_collection('slot_requests').find_one({'_id': request_object_id})
    if not stored_request:
        raise HTTPException(status_code=404, detail='Slot request not found')
    if stored_request.get('status') == 'closed':
        raise HTTPException(status_code=409, detail='Closed slot request cannot be confirmed')

    selected_slot = None
    if confirmation.date or confirmation.time:
        if not confirmation.date or not confirmation.time:
            raise HTTPException(status_code=400, detail='Both date and time are required')
        selected_slot = {'date': confirmation.date, 'time': confirmation.time}

    stored_request['_id'] = request_object_id
    try:
        result = confirm_slot_request(stored_request, selected_slot)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    return {'requestId': request_id, **result}


@router.post('/{request_id}/close')
def officer_close_slot_request(request_id: str, closure: OfficerClosure):
    request_object_id = _object_id(request_id, 'requestId')
    collection = get_collection('slot_requests')
    stored_request = collection.find_one({'_id': request_object_id})
    if not stored_request:
        raise HTTPException(status_code=404, detail='Slot request not found')
    if stored_request.get('status') == 'confirmed':
        raise HTTPException(status_code=409, detail='Confirmed slot request cannot be closed')
    if stored_request.get('status') == 'closed':
        return {'requestId': request_id, 'status': 'closed', 'message': 'Slot request is already closed'}

    now = datetime.now(timezone.utc)
    collection.update_one(
        {'_id': request_object_id},
        {'$set': {
            'status': 'closed',
            'closeReason': closure.reason,
            'closedAt': now,
            'updatedAt': now,
        }},
    )
    return {'requestId': request_id, 'status': 'closed', 'reason': closure.reason}
