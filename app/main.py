from typing import Annotated
from fastapi import FastAPI, HTTPException, status, Depends, Form, UploadFile, File
from sqlmodel import Session
from capsule_handler import MessageMeta, parse_message_meta , image_validation
from db import create_db_and_tables, get_session, save_capsule_in_db, Capsule

app = FastAPI()

# crear la base de datos al iniciar la app
@app.on_event("startup")
def on_startup():
    create_db_and_tables()


"""
idea: validar si se intenta enviar una imagen o un texto, 
luego guardar en una variable ese string que contendra la
url de la imagen o el texto dependiendo que se elija enviar
"""

@app.post("/message/")
async def send(
               session: Annotated[Session, Depends(get_session)],
               msg_metadata: Annotated[MessageMeta, Depends(parse_message_meta)], 
               msg_text: str | None = Form(None), # -> si es texto
               file:  UploadFile | None = File(None), # -> si es una imagen
               ) -> Capsule:
    
    try:
        contents = await image_validation(file)
        capsule = save_capsule_in_db(msg_metadata, contents, session)
        return capsule
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Internal Server Error")
    
    

