from pydantic import EmailStr
from sqlmodel import Field, SQLModel, Relationship
from uuid import UUID, uuid4
from datetime import datetime
from typing import List
from enum import Enum

class RepairStatus(str, Enum):
    pendiente = "pendiente"
    en_reparacion = "en_reparacion"
    listo = "listo"
    entregado = "entregado"

class Mechanic(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    phone: str = Field(index=True)

    repairs: List["Repairs"] = Relationship(back_populates="mechanics")
    

class Client(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    phone_number: str = Field(index=True)
    email: EmailStr = Field(index=True, max_length=255)

    vehicles: List["Vehicle"] = Relationship(back_populates="client")


class Vehicle(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    license_plate: str = Field(index=True, unique=True)
    brand: str = Field(index=True)
    model: str = Field(index=True)
    year: int = Field(index=True)

    client_id: UUID = Field(foreign_key="client.id")
    client: Client | None = Relationship(back_populates="vehicles")

    repairs: List["Repairs"] = Relationship(back_populates="vehicles")


class Repairs(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    description: str = Field(index=True)
    status: RepairStatus = Field(index=True)
    start_date: datetime = Field(index=True)
    finish_date: datetime = Field(index=True)

    mechanic_id: UUID = Field(foreign_key="mechanic.id")
    mechanics: Mechanic | None = Relationship(back_populates="repairs")

    vehicle_id: UUID = Field(foreign_key="vehicle.id")
    vehicles: Vehicle | None = Relationship(back_populates="repairs")

    records: List["Record"] = Relationship(back_populates="repairs")


class Record(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    date: datetime = Field(index=True)
    description: str = Field(index=True)
    status: str = Field(index=True)

    repair_id: UUID = Field(foreign_key="repairs.id")
    repairs: Repairs | None = Relationship(back_populates="records")

