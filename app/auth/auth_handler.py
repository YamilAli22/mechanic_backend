import time
from typing import Annotated, cast
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from app.models import Mechanic
from app.schemas.mechanic import MechanicRead
import jwt
from decouple import config
from app.db import Session, get_session

JWT_SECRET = cast(str, config("secret"))
JWT_ALGORITHM = cast(str, config("algorithm"))

class TokenResponse(BaseModel): 
    access_token: str
    token_type: str
    mechanic: MechanicRead

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/mechanic/login")

def token_response(token: str):
    return {
        "access_token": token,
        "token_type": "bearer"
    }

def sign_jwt(mechanic: Mechanic) -> str:
    payload = {
        "sub": str(mechanic.id),
        "email": mechanic.email,
        "exp": int(time.time()) + 900
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_jwt(token: str) -> dict | None:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except:
        return {}

async def get_current_mechanic(session: Annotated[Session, Depends(get_session)], 
                               token: Annotated[str, Depends(oauth2_scheme)]
) -> Mechanic:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_jwt(token)
    if not payload:
        raise HTTPException(status_code=401)

    mechanic_id = payload["sub"]
    if not mechanic_id:
        raise credentials_exception

    mechanic = session.get(Mechanic, mechanic_id)
    if not mechanic or mechanic.deleted_at is not None:
        raise credentials_exception
    return mechanic




