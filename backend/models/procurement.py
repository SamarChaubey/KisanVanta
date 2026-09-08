from datetime import datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class ProcurementRequest(BaseModel):
    crop: str
    quantity: float


class ProcurementQuality(BaseModel):
    status: str
    grade: str


class ProcurementRecord(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)

    id: ObjectId = Field(alias='_id')
    farmerId: ObjectId
    slotRequestId: ObjectId
    centreId: ObjectId
    crop: str
    quantity: float
    queueNumber: int
    status: str
    quality: ProcurementQuality
    expectedValue: float
    actualValue: Optional[float] = None
    createdAt: datetime
    updatedAt: datetime
