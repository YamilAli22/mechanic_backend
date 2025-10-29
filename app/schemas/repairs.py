from pydantic import BaseModel
from datetime import datetime

from app.models import RepairStatus

class Repairs(BaseModel):
    description: str
    status: RepairStatus
    start_date: datetime
    finish_date: datetime
