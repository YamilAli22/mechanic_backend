from typing import Optional
from pydantic import BaseModel
from uuid import UUID

class VehicleCreate(BaseModel):
    license_plate: str
    brand: str
    model: str
    year: int
    client_id: UUID

class VehicleRead(BaseModel):
    id: UUID
    license_plate: str
    brand: str
    model: str
    year: int
    client_id: UUID

    model_config = {
        "from_attributes": True
    }

class VehicleUpdate(BaseModel):
    license_plate: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
