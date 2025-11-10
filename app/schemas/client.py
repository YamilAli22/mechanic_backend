from pydantic import BaseModel, EmailStr
from uuid import UUID

class ClientCreate(BaseModel):
    name: str
    phone_number: str
    email: EmailStr

class ClientRead(BaseModel):
    id: UUID
    name: str
    phone_number: str
    email: EmailStr

    model_config = {
        "from_attributes": True
    } # esto sirve para que la api me devuelva un JSON a partir de un objeto SQLModel
