from uuid import UUID
from fastapi import Depends
from typing import Annotated
from models import Vehicle, Client
from sqlmodel import select, Session 
from db import SessionDep, get_session

async def get_vehicle_data(session: Annotated[Session, Depends(get_session)], vehicle_id: UUID) -> Vehicle | None:
    try:
        vehicle = session.exec(select(Vehicle).filter(Vehicle.id == vehicle_id)).one_or_none()
        if vehicle:
            return vehicle
        return None
    finally:
        session.close()

async def search_vehicles(
        session: Annotated[Session, Depends(get_session)], 
        q: str | None, 
        vehicle_code: str | None, 
        limit: int = 20
) -> list[Vehicle]:
    try:
        if not q and not vehicle_code:
            return []
        
        query = select(Vehicle).join(Client)

        conditions = []

        if q:
            conditions.append(Client.name.ilike(f"%{q}%")) # type: ignore
        if vehicle_code:
            conditions.append(Vehicle.license_plate.ilike(f"%{vehicle_code}%")) # type: ignore
        
        if conditions:
            query = query.where(*conditions) # -> el * desempaqueta lo que hay en la lista
        
        query = query.order_by(Client.name).limit(limit)
        result = session.exec(query).all()
        return result
    
    finally:
        session.close()
            


