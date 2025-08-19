from fastapi import HTTPException, status, UploadFile, File, Form
from pydantic import BaseModel, EmailStr
from enum import Enum
import imghdr
from uuid import UUID
from datetime import datetime

class ContentType(str, Enum):
    text = "text"
    image = "image"

class MessageMeta(BaseModel):
    email: EmailStr
    unlock_date: datetime
    content_type: ContentType
    sender_id: UUID | None = None

# esto sirve para que fastAPI no se queje porque le pasamos Form/File y BaseModel(JSON)
# en el endpoint, entonces parseamos el MessageData que es un BaseModel a Form (o File si hiciera falta)
def parse_message_meta(email: EmailStr = Form(...),
                       unlock_date: datetime = Form(...),
                       content_type: ContentType = Form(...),
                       sender_id: UUID | None = Form(...)) -> MessageMeta:
    return MessageMeta(
        email=email,
        unlock_date=unlock_date,
        content_type=content_type,
        sender_id=sender_id
    )

async def image_validation(file: UploadFile):
    try:
        contents = await file.read()
        allowed_types = ["jpeg", "png", "gif"]
        mime_type = imghdr.what(None, h=contents)
        
        if mime_type not in allowed_types:
            raise HTTPException(status_code=400,
                                detail=f'Forbidden image format: {mime_type}')
        return contents
    except FileNotFoundError:
        return(f"Error: The file {file} was not found.")
    except Exception as e:
        return(f"An error occurred: {e}")



