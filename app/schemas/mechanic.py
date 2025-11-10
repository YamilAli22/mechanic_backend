from pydantic import BaseModel
from uuid import UUID

class MechanicCreate(BaseModel):
    name: str
    phone: str

class MechanicRead(BaseModel):
    id: UUID
    name: str
    phone: str

    model_config = {
        'from_attributes': True
    }