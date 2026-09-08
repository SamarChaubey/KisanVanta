from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from services.farmer_query import answer_farmer_query
from typing import Literal

from database import get_collection

router = APIRouter()


def _object_id(value):
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        raise HTTPException(status_code=400, detail='Invalid farmerId') from None


def _stringify(doc):
    doc = dict(doc)
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            doc[key] = str(value)
    return doc


@router.get('/{farmer_id}/status')
def get_farmer_status(farmer_id: str):
    oid = _object_id(farmer_id)
    farmer = get_collection('users').find_one({'_id': oid})
    if not farmer:
        raise HTTPException(status_code=404, detail='Farmer not found')

    slot_requests = [_stringify(d) for d in get_collection('slot_requests').find({'farmerId': oid})]
    procurement_records = [_stringify(d) for d in get_collection('procurement_records').find({'farmerId': oid})]
    financial_exposure = [_stringify(d) for d in get_collection('financial_exposure').find({'farmerId': oid})]

    return {
        'farmer': _stringify(farmer),
        'slotRequests': slot_requests,
        'procurementRecords': procurement_records,
        'financialExposure': financial_exposure,
    }
class FarmerQuestion(BaseModel):
    question: str
    language: Literal['en', 'hi'] = Field(
        default='en',
        description='Response language: en for English or hi for Hindi.',
    )


@router.post('/{farmer_id}/ask')
def ask_farmer_question(farmer_id: str, payload: FarmerQuestion):
    try:
        answer = answer_farmer_query(farmer_id, payload.question, payload.language)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return {
        'farmerId': farmer_id,
        'question': payload.question,
        'language': payload.language,
        'answer': answer,
    }