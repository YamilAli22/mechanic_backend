from datetime import datetime, timezone
from uuid import UUID
from fastapi import Depends, HTTPException
from typing import Annotated
from models import Vehicle, Client
from schemas.vehicle import VehicleRead, VehicleUpdate
from sqlmodel import select, Session 
from db import get_session

async def get_vehicle_data(session: Annotated[Session, Depends(get_session)], vehicle_id: UUID) -> Vehicle | None:
    vehicle = session.exec(select(Vehicle).filter(Vehicle.id == vehicle_id)).one_or_none()
    if vehicle:
        return vehicle
    return None

async def search_vehicles(
        session: Annotated[Session, Depends(get_session)], 
        q: str | None, 
        vehicle_code: str | None, 
        limit: int = 20
) -> list[Vehicle]:
    if not q and not vehicle_code:
        return []
        
    query = select(Vehicle).where(Vehicle.deleted_at==None).join(Client)

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

            
async def update_vehicle(session: Annotated[Session, Depends(get_session)], vehicle_id: UUID, update: VehicleUpdate) -> VehicleRead:
    query = select(Vehicle).where(Vehicle.id==vehicle_id, Vehicle.deleted_at==None)
    vehicle = session.exec(query).first()

    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(vehicle, key, value)

    session.add(vehicle)
    session.commit()
    session.refresh(vehicle)

    return vehicle 

async def delete_vehicle(session: Annotated[Session, Depends(get_session)], vehicle_id: UUID):
    vehicle = session.get(Vehicle, vehicle_id)

    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    vehicle.deleted_at = datetime.now(timezone.utc)

    session.add(vehicle)
    session.commit()
    session.refresh(vehicle)

    return None
 
