import time
from typing import Dict, cast
from uuid import UUID
import jwt
from decouple import config
from pydantic import EmailStr

JWT_SECRET = cast(str, config("secret"))
JWT_ALGORITHM = cast(str, config("algorithm"))

def token_response(token: str):
    return {
        "access_token": token
    }

def sign_jwt(mechanic_email: EmailStr) -> Dict[str, str]:
    payload = {
        "mechanic_email": mechanic_email,
        "expires": time.time() + 900
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token_response(token)

def decode_jwt(token: str) -> dict | None:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except:
        return {}




