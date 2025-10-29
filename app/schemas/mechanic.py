from pydantic import BaseModel

class Mechanic(BaseModel):
    name: str
    phone: str