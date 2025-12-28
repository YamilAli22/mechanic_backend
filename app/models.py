from pydantic import EmailStr
from sqlmodel import Field, SQLModel, Relationship
from uuid import UUID, uuid4
from datetime import datetime
from typing import List, Optional
from app.schemas.repairs import RepairStatus

class Mechanic(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    email: EmailStr = Field(index=True, max_length=255)
    password: str = Field(index=True)
    phone: str = Field(index=True)
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)

    repairs: List["Repairs"] = Relationship(back_populates="mechanics")
    

class Client(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    phone_number: str = Field(index=True)
    email: EmailStr = Field(index=True, max_length=255)
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)

    vehicles: List["Vehicle"] = Relationship(back_populates="client")


class Vehicle(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    license_plate: str = Field(index=True, unique=True)
    brand: str = Field(index=True)
    model: str = Field(index=True)
    year: int = Field(index=True)
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)

    client_id: UUID = Field(foreign_key="client.id")
    client: Client | None = Relationship(back_populates="vehicles")

    repairs: List["Repairs"] = Relationship(back_populates="vehicles")


class Repairs(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    description: Optional[str] = Field(index=True, default=None)
    status: RepairStatus = Field(index=True, default=RepairStatus.pendiente)
    start_date: datetime = Field(index=True)
    finish_date: datetime = Field(index=True) 
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)

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

