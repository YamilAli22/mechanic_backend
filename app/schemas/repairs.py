from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from enum import Enum

class RepairStatus(str, Enum):
    pendiente = "pendiente"
    en_reparacion = "en_reparacion"
    listo = "listo"
    entregado = "entregado"

class RepairsCreate(BaseModel):
    description: str
    start_date: datetime
    finish_date: datetime

    mechanic_id: UUID
    vehicle_id: UUID

class RepairsRead(BaseModel):
    id: UUID
    description: str
    status: RepairStatus
    start_date: datetime
    finish_date: datetime

    mechanic_id: UUID
    vehicle_id: UUID

    model_config = {
        "from_attributes": True
    }

