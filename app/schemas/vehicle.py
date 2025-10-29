from pydantic import BaseModel

class Vehicle(BaseModel):
    license_plate: str
    brand: str
    model: str
    year: int