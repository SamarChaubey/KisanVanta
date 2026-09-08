from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter
from fastapi import HTTPException
from pydantic import BaseModel

from database import get_collection
from services.booking_service import BookingSystemError
from services.scheduler import accept_alternative, schedule_slot

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


def _object_id(value, field_name):
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        raise HTTPException(status_code=400, detail=f'Invalid {field_name}') from None


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
