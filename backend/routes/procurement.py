from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from database import get_collection
from models.procurement import ProcurementRequest
from services.centre_status_service import recompute_centre_status

router = APIRouter()

VALID_TRANSITIONS = {
    'waiting': {'assaying'},
    'assaying': {'weighing', 'rejected'},
    'weighing': {'accepted', 'downgraded', 'rejected'},
    'accepted': {'completed'},
    'downgraded': {'completed'},
    'rejected': set(),
    'completed': set(),
}


class QualityUpdate(BaseModel):
    status: str
    grade: str = ''
    actualValue: float | None = None


class CompletionUpdate(BaseModel):
    actualValue: float | None = None


def _object_id(value):
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        raise HTTPException(status_code=400, detail='Invalid recordId') from None


@router.post('/')
def create_procurement_request(request: ProcurementRequest):
    return {'status': 'received', 'request': request}


@router.patch('/{record_id}/status')
def update_procurement_status(record_id: str, update: QualityUpdate):
    oid = _object_id(record_id)
    record = get_collection('procurement_records').find_one({'_id': oid})
    if not record:
        raise HTTPException(status_code=404, detail='Procurement record not found')

    current_status = record['status']
    allowed_next = VALID_TRANSITIONS.get(current_status, set())
    if update.status not in allowed_next:
        raise HTTPException(
            status_code=400,
            detail=f'Cannot move from {current_status} to {update.status}',
        )

    set_fields = {
        'status': update.status,
        'quality.status': update.status,
        'updatedAt': datetime.now(timezone.utc),
    }
    if update.grade:
        set_fields['quality.grade'] = update.grade
    if update.actualValue is not None:
        set_fields['actualValue'] = update.actualValue

    get_collection('procurement_records').update_one({'_id': oid}, {'$set': set_fields})
    recompute_centre_status(record['centreId'])

    return {'status': 'updated', 'recordId': record_id, 'newStatus': update.status}


@router.patch('/{record_id}/complete')
def complete_procurement(record_id: str, update: CompletionUpdate):
    oid = _object_id(record_id)
    records = get_collection('procurement_records')
    record = records.find_one({'_id': oid})
    if not record:
        raise HTTPException(status_code=404, detail='Procurement record not found')
    if record['status'] == 'completed':
        return {
            'status': 'completed',
            'recordId': record_id,
            'message': 'Procurement is already complete',
        }
    if record['status'] not in {'accepted', 'downgraded'}:
        raise HTTPException(
            status_code=409,
            detail='Only accepted or downgraded procurements can be completed',
        )

    now = datetime.now(timezone.utc)
    set_fields = {'status': 'completed', 'updatedAt': now, 'completedAt': now}
    if update.actualValue is not None:
        set_fields['actualValue'] = update.actualValue
    records.update_one({'_id': oid}, {'$set': set_fields})

    get_collection('slot_requests').update_one(
        {'_id': record['slotRequestId']},
        {'$set': {'status': 'completed', 'updatedAt': now}},
    )
    recompute_centre_status(record['centreId'])
    return {
        'status': 'completed',
        'recordId': record_id,
        'actualValue': update.actualValue,
    }
