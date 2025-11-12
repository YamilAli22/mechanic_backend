from uuid import UUID
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

async def search_mechanics(session: SessionDep, q: str | None = None) -> list[Mechanic]:
    try:
        query = select(Mechanic)

        if q:
            query = query.where(Mechanic.name.ilike(f"%{q}%"))

        mechanics = session.exec(query).all()
        return mechanics
    finally:
        session.close()