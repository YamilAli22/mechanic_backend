from typing import Optional
from pydantic import BaseModel, EmailStr
from uuid import UUID

class MechanicCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: str

class MechanicRead(BaseModel):
    id: UUID
    name: str
    phone: str
 
    model_config = {
        'from_attributes': True
    }

class MechanicUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
