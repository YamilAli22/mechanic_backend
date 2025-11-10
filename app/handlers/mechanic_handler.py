from uuid import UUID
from fastapi import HTTPException
from models import Mechanic
from sqlmodel import select
from db import SessionDep

async def get_mechanic_data(session: SessionDep, mechanic_id: UUID) -> Mechanic:
    try:
        data = session.exec(select(Mechanic).filter(Mechanic.id==mechanic_id)).one_or_none()
        if data:
            return data
        return None
    finally:
        session.close()