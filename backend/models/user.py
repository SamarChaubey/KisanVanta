from datetime import datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class User(BaseModel):
    name: str
    phone: str


class UserDocument(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)

    id: ObjectId = Field(alias='_id')
    name: str
    phone: str
    role: str
    village: Optional[str] = None
    fpoId: Optional[ObjectId] = None
    centreId: Optional[ObjectId] = None
    createdAt: datetime
    updatedAt: Optional[datetime] = None
