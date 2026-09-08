from bson import ObjectId
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class ProcurementCentre(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)

    id: ObjectId = Field(alias='_id')
    name: str
    location: dict[str, str]
    crops: list[str]
    dailyCapacity: int
    processingRate: int
    storageCapacity: int
    currentStorage: int
    liftingCapacity: int
    status: str


class BookingSlot(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)

    id: ObjectId = Field(alias='_id')
    centreId: ObjectId
    date: str
    time: str
    capacity: int
    booked: int
    status: str
