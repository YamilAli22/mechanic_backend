from datetime import datetime, timezone
from uuid import UUID
from fastapi import HTTPException, Depends
from app.schemas.repairs import RepairsUpdate, RepairStatus
from app.models import Repairs, Vehicle, Client
from sqlmodel import select, Session
from typing import Annotated, Sequence
from app.db import get_session

async def get_repair_data(session: Annotated[Session, Depends(get_session)], repair_id: UUID) -> Repairs | None:
    data = session.exec(select(Repairs).where(Repairs.id==repair_id)).one_or_none()
    return data

async def search_repairs(
        session: Annotated[Session, Depends(get_session)], 
        license_plate: str | None = None, 
        client_name: str | None = None,
        status: RepairStatus | None = None,
        limit: int = 20
) -> Sequence[Repairs]:
    if not license_plate and not client_name:
        return []
        
    query = select(Repairs).where(Repairs.deleted_at==None).join(Vehicle).join(Client)
        
    conditions = []

    if license_plate:
        conditions.append(Vehicle.model.ilike(f"%{license_plate}%")) # type: ignore
    if client_name:
        conditions.append(Client.name.ilike(f"%{client_name}%")) # type: ignore
    if status:
        conditions.append(Repairs.status == status)      
    if conditions:
        query = query.where(*conditions)
        
    query = query.order_by(str(Repairs.start_date)).limit(limit)
    result = session.exec(query).all()
    return result

async def update_info(session: Annotated[Session, Depends(get_session)], repair_id: UUID, update: RepairsUpdate) -> Repairs:
    query = select(Repairs).where(Repairs.id==repair_id, Repairs.deleted_at==None)
    repair = session.exec(query).first()

    if not repair:
        raise HTTPException(status_code=404, detail="Repair not found")
        
    repair.description = update.description
    repair.status = update.status
    session.add(repair)
    session.commit()
    session.refresh(repair)

    return repair


async def delete_repair(session: Annotated[Session, Depends(get_session)], repair_id: UUID):
    repair = session.get(Repairs, repair_id)

    if not repair:
        raise HTTPException(status_code=404, detail="Repair not found")

    repair.deleted_at = datetime.now(timezone.utc)

    session.add(repair)
    session.commit()
    session.refresh(repair)

    return None
 
