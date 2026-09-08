from fastapi import APIRouter

from models.slot_request import SlotRequest

router = APIRouter()


@router.post('/')
def create_slot_request(request: SlotRequest):
    return {'status': 'received', 'request': request}
