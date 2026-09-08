from typing import Literal

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from database import get_collection
from services.operational_context import gather_operational_context
from services.ollama_client import generate_answer

router = APIRouter()


class AdminQuestion(BaseModel):
    question: str = Field(min_length=1)
    centreId: str | None = None
    language: Literal['en', 'hi'] = 'en'


class CentreAdminQuestion(BaseModel):
    question: str = Field(min_length=1)
    language: Literal['en', 'hi'] = 'en'


def _object_id(value):
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        raise HTTPException(status_code=400, detail='Invalid centreId') from None


def _answer_question(question, language, context):
    language_instruction = (
        'Respond entirely in Hindi using Devanagari script.'
        if language == 'hi'
        else 'Respond entirely in clear, concise English.'
    )
    prompt = (
        'You are an operations advisor for agricultural procurement officers. '
        'Use only the live operational data provided below. '
        'Assess current queues, capacity, storage, lifting, available slots, and active alerts. '
        'Identify upcoming bottlenecks, explain the uncertainty of any prediction, '
        'and recommend concrete precautions and the best available slot when relevant. '
        'Never guarantee a slot or invent data. State when data is missing or stale. '
        f'{language_instruction}\n\n'
        f'Operational data:\n{context}\n\n'
        f"Officer's question: {question}\n\n"
        'Answer with: situation, risks, confidence/uncertainty, and recommended actions.'
    )
    try:
        return generate_answer(prompt)
    except Exception as error:
        raise HTTPException(status_code=503, detail='AI service unavailable') from error


@router.post('/ask')
def ask_admin_question(payload: AdminQuestion):
    centre_id = _object_id(payload.centreId) if payload.centreId else None
    context = gather_operational_context(centre_id)
    answer = _answer_question(payload.question, payload.language, context)

    return {
        'question': payload.question,
        'centreId': payload.centreId,
        'language': payload.language,
        'answer': answer,
    }


@router.post('/centres/{centre_id}/ask')
def ask_centre_admin_question(centre_id: str, payload: CentreAdminQuestion):
    centre_object_id = _object_id(centre_id)
    centre = get_collection('procurement_centres').find_one({'_id': centre_object_id})
    if not centre:
        raise HTTPException(status_code=404, detail='Centre not found')

    context = gather_operational_context(centre_object_id)
    answer = _answer_question(payload.question, payload.language, context)
    return {
        'centreId': centre_id,
        'question': payload.question,
        'language': payload.language,
        'answer': answer,
    }