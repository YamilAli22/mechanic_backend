from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.exc import IntegrityError
from typing import Annotated
from fastapi import Depends, HTTPException, status
from schemas.client import ClientCreate
from schemas.vehicle import VehicleCreate
from schemas.repairs import RepairsCreate, RepairStatus
from schemas.mechanic import MechanicCreate
from models import Mechanic, Client, Vehicle, Repairs

sql_filename = "database.db"
sql_url = f"sqlite:///{sql_filename}"

connect_args = {"check_same_thread": False}
engine = create_engine(sql_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

def save_mechanic_in_db(session: Session, mechanic_data: MechanicCreate) -> Mechanic:
    mechanic = Mechanic(
        name=mechanic_data.name,
        phone=mechanic_data.phone
    )
    session.add(mechanic)
    session.commit()
    session.refresh(mechanic)
    return mechanic

def save_client_in_db(client_data: ClientCreate, session: Session) -> Client:
    client = Client(
                    name=client_data.name,
                    phone_number=client_data.phone_number,
                    email=client_data.email
                    )
    session.add(client)
    session.commit()
    session.refresh(client)
    return client


def save_vehicle_in_db(session: Session, vehicle_data: VehicleCreate) -> Vehicle:
    client = session.get(Client, vehicle_data.client_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    
    vehicle = Vehicle(
        license_plate=vehicle_data.license_plate,
        brand=vehicle_data.brand,
        model=vehicle_data.model,
        year=vehicle_data.year,
        client_id=vehicle_data.client_id
    )

    session.add(vehicle)

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="License plate must be unique")
    
    session.refresh(vehicle)
    return vehicle

def save_repair_in_db(session: Session, repair_data: RepairsCreate) -> Repairs:
    vehicle = session.get(Vehicle, repair_data.vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
    
    repair = Repairs(
        description=repair_data.description,
        status=RepairStatus.pendiente,
        start_date=repair_data.start_date,
        finish_date=repair_data.finish_date,
        mechanic_id=repair_data.mechanic_id,
        vehicle_id=repair_data.vehicle_id
    )

    session.add(repair)
    session.commit()
    session.refresh(repair)
    return repair




