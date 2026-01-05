from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from enum import Enum

class RepairStatus(str, Enum):
    pendiente = "pending"
    en_reparacion = "in repair"
    listo = "ready"
    entregado = "delivered"

class RepairsUpdate(BaseModel):
    description: Optional[str] = None
    status: RepairStatus

class RepairsCreate(BaseModel):
    description: str
    start_date: datetime
    finish_date: datetime

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

