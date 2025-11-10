from uuid import UUID
from fastapi import HTTPException
from schemas.repairs import RepairStatus, RepairsCreate
from models import Repairs
from sqlmodel import select
from db import SessionDep

async def get_repair_data(session: SessionDep, repair_id: UUID) -> Repairs:
    try:
        data = session.exec(select(Repairs).filter(Repairs.id==repair_id)).one_or_none()
        if data:
            return data
        return None
    finally:
        session.close()

async def update_info(session: SessionDep, repair_id: UUID, status: RepairStatus, info: RepairsCreate):
    try:
        repair = session.get(Repairs, repair_id)

        if not repair:
            raise HTTPException(status_code=404, detail="Repair not found")
        
        repair.status = status
        repair.description = info.description
        session.add(repair)
        session.commit()
        session.refresh(repair)

        return repair
    finally:
        session.close()


