from pydantic import BaseModel


class SlotRequest(BaseModel):
    farmer_id: str
    centre_id: str
