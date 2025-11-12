from uuid import UUID
from models import Client
from sqlmodel import select
from db import SessionDep

async def get_client_data(client_id: UUID, session: SessionDep) -> Client:
    try:
        data = session.exec(select(Client).filter(Client.id == client_id)).one_or_none()
        if data:
            return data
        return None
    finally:
        session.close()

# async def get_clients_list(session: SessionDep) -> list[Client]:
#     try:
#         clients_list = []
#         data = session.exec(select(Client))
#         if data:
#             for row in data:
#                 clients_list.append(row)
#         return clients_list
#     finally:
#         session.close()

async def search_clients(session: SessionDep, q: str | None = None, limit: int = 20) -> list[Client]:
    try:
        query = select(Client)

        if q:
            query = query.where(Client.name.ilike(f"%{q}%"))
    
        query = query.order_by(Client.name).limit(limit)
        clients = session.exec(query).all()
        return clients
    
    finally:
        session.close

