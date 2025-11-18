from uuid import UUID
from typing import Annotated
from fastapi import Depends
from models import Client
from sqlmodel import select, Session
from db import get_session

async def get_client_data(client_id: UUID, session: Annotated[Session, Depends(get_session)]) -> Client | None:
    try:
        data = session.exec(select(Client).filter(Client.id == client_id)).one_or_none()
        if data:
            return data
        return None
    finally:
        session.close()

async def search_clients(session: Annotated[Session, Depends(get_session)], q: str | None = None, limit: int = 20) -> list[Client]:
    try:
        query = select(Client)

        if q:
            query = query.where(Client.name.ilike(f"%{q}%")) # type: ignore
    
        query = query.order_by(Client.name).limit(limit)
        clients = session.exec(query).all()
        return clients
    
    finally:
        session.close

