from uuid import UUID
from models import Vehicle
from sqlmodel import select
from db import SessionDep

async def get_vehicle_data(session: SessionDep, vehicle_code: str) -> Vehicle:
    try:
        data = session.exec(select(Vehicle).filter(Vehicle.license_plate==vehicle_code)).one_or_none()
        if data: 
            return data
        return None
    finally:
        session.close()