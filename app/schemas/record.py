from pydantic import BaseModel
from datetime import datetime

class Record(BaseModel):
    date: datetime
    description: str
    status: str