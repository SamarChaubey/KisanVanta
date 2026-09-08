from pydantic import BaseModel


class ProcurementRequest(BaseModel):
    crop: str
    quantity: float
