from uuid import UUID
from typing import Annotated
from models import Mechanic
from sqlmodel import select, Session
from fastapi import Depends
from db import get_session

async def get_mechanic_data(session: Annotated[Session, Depends(get_session)], mechanic_id: UUID) -> Mechanic | None:
    try:
        data = session.exec(select(Mechanic).filter(Mechanic.id==mechanic_id)).one_or_none()
        if data:
            return data
        return None
    finally:
        session.close()

async def search_mechanics(session:  Annotated[Session, Depends(get_session)], q: str | None = None) -> list[Mechanic]:
    try:
        query = select(Mechanic)

        if q:
            query = query.where(Mechanic.name.ilike(f"%{q}%")) # type: ignore

        mechanics = session.exec(query).all()
        return mechanics
    finally:
        session.close()
