from datetime import datetime, timezone
from uuid import UUID
from typing import Annotated, Sequence

from app.models import Mechanic
from app.schemas.mechanic import MechanicUpdate, MechanicLogin
from sqlmodel import select, Session
from fastapi import Depends, HTTPException
from app.db import get_session
from app.auth.security import hash_pwd, verify_pwd

async def check_mechanic(session: Annotated[Session, Depends(get_session)], username: str, password: str) -> Mechanic | None:
    query = select(Mechanic).where(Mechanic.email==username, Mechanic.deleted_at==None)
    mechanic = session.exec(query).one_or_none()

    if mechanic and verify_pwd(password, mechanic.password):
        return mechanic
    
    return None

async def get_mechanic_data(session: Annotated[Session, Depends(get_session)], mechanic_id: UUID) -> Mechanic | None:   
    data = session.exec(select(Mechanic).where(Mechanic.id==mechanic_id)).one_or_none()
    return data

  
async def search_mechanics(session:  Annotated[Session, Depends(get_session)], q: str | None = None) -> Sequence[Mechanic]:
    query = select(Mechanic).where(Mechanic.deleted_at == None)

    if q:
        query = query.where(Mechanic.name.ilike(f"%{q}%")) # type: ignore

    mechanics = session.exec(query).all()
    return mechanics
     
async def update_mechanic(session: Annotated[Session, Depends(get_session)], mechanic_id: UUID, update: MechanicUpdate) -> Mechanic:
    query = select(Mechanic).where(Mechanic.id==mechanic_id, Mechanic.deleted_at==None)

    mechanic = session.exec(query).first()
    if not mechanic:
        raise HTTPException(status_code=404, detail="Mechanic not found")

    update_data = update.model_dump(exclude_unset=True)
    
    if "password" in update_data:
        update_data["password"] = hash_pwd(update_data["password"]) # -> quizás hacer una función y endpoint aparte para actualizas pwd

    for key, value in update_data.items():
        setattr(mechanic, key, value)

    session.add(mechanic)
    session.commit()
    session.refresh(mechanic)        
    
    return mechanic

async def delete_mechanic(session: Annotated[Session, Depends(get_session)], mechanic_id: UUID):
    mechanic = session.get(Mechanic, mechanic_id)

    if not mechanic:
        raise HTTPException(status_code=404, detail="Mechanic not found")

    mechanic.deleted_at = datetime.now(timezone.utc)

    session.add(mechanic)
    session.commit()
    session.refresh(mechanic)

    return None
    


