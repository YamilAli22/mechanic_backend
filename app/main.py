from contextlib import asynccontextmanager
from typing import Annotated
from sqlmodel import Session

from fastapi import FastAPI, Depends, HTTPException, status
from db import create_db_and_tables, get_session, save_client_in_db
from schemas.client import ClientCreate, ClientRead

# esto deberia ejecutarse antes de que la app empieze a recibir requests
# es decir, lo primero que quiero hacer es crear la base de datos
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield # deberia ir algo luego de este yield?

app = FastAPI(lifespan=lifespan)

# endpoints

@app.post("/clients/", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
def create_client(
    session: Annotated[Session, Depends(get_session)],
    client_data: ClientCreate
):
    try:
        return save_client_in_db(client_data, session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))

    
    


    
    

