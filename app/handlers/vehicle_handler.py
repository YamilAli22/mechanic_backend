from uuid import UUID
from models import Vehicle, Client
from sqlmodel import select
from db import SessionDep

async def get_client_vehicles(session: SessionDep, client_id: UUID) -> list[Vehicle]:
    try:
        client_vehicles = []
        data = session.exec(select(Vehicle).filter(Client.id == client_id)).all()
        if data:
            for row in data:
                client_vehicles.append(row)
        return client_vehicles
    finally:
        session.close()

async def get_vehicle_data(session: SessionDep, client_id: UUID, vehicle_code: str) -> Vehicle:
    try:
        data = session.exec(select(Vehicle).filter(Vehicle.license_plate==vehicle_code 
                                                and Vehicle.client_id==client_id)).one_or_none()
        if data: 
            return data
        return None
    finally:
        session.close()
