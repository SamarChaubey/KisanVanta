from pydantic import BaseModel


class Centre(BaseModel):
    name: str
    location: str
