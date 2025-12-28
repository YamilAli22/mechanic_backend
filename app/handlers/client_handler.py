from datetime import datetime, timezone
from uuid import UUID
from typing import Annotated, Sequence
from fastapi import Depends, HTTPException

from app.models import Client
from app.schemas.client import ClientUpdate
from sqlmodel import select, Session
from app.db import get_session

async def get_client_data(client_id: UUID, session: Annotated[Session, Depends(get_session)]) -> Client | None:
    data = session.exec(select(Client).where(Client.id == client_id)).one_or_none()
    if data:
        return data
    return None

async def search_clients(session: Annotated[Session, Depends(get_session)], q: str | None = None, limit: int = 20) -> Sequence[Client]:
    query = select(Client).where(Client.deleted_at==None)

    if q:
        query = query.where(Client.name.ilike(f"%{q}%")) # type: ignore
    
    query = query.order_by(Client.name).limit(limit)
    clients = session.exec(query).all()
    return clients

async def update_client(session: Annotated[Session, Depends(get_session)], client_id: UUID, update: ClientUpdate) -> Client:
    query = select(Client).where(Client.id==client_id, Client.deleted_at==None)
    client = session.exec(query).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(client, key, value)

    session.add(client)
    session.commit()
    session.refresh(client)

    return client 

async def delete_client(session: Annotated[Session, Depends(get_session)], client_id: UUID):
    client = session.get(Client, client_id)

    if not client:
        raise HTTPException(status_code=404, detail="Mechanic not found")

    client.deleted_at = datetime.now(timezone.utc)

    session.add(client)
    session.commit()
    session.refresh(client)

    return None
 







