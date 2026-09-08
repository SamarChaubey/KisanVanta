from datetime import datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class SlotReference(BaseModel):
    date: str
    time: str


class SlotRequestDocument(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)

    id: ObjectId = Field(alias='_id')
    farmerId: ObjectId
    centreId: ObjectId
    crop: str
    quantity: float
    requestedDate: str
    preferredTime: str
    status: str
    requestedSlot: SlotReference
    suggestedSlot: Optional[SlotReference] = None
    finalSlot: Optional[SlotReference] = None
    createdAt: datetime
    updatedAt: datetime
