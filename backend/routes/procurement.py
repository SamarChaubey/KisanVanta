from fastapi import APIRouter

from models.procurement import ProcurementRequest

router = APIRouter()


@router.post('/')
def create_procurement_request(request: ProcurementRequest):
    return {'status': 'received', 'request': request}
