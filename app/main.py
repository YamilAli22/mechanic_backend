from contextlib import asynccontextmanager
from typing import Optional
from uuid import UUID
from handlers import client_handler, vehicle_handler

from fastapi import FastAPI, HTTPException, status
from db import create_db_and_tables, save_client_in_db, save_vehicle_in_db, SessionDep
from schemas.client import *
from schemas.vehicle import *

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
    session: SessionDep,
    client_data: ClientCreate
):
    try:
        return save_client_in_db(client_data, session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))
    

    
@app.get("/clients/{client_id}", response_model=Optional[ClientRead], status_code=status.HTTP_200_OK)
async def search_client(session: SessionDep, client_id: UUID):
    try:
        client_data = await client_handler.get_client_data(client_id, session)
        return client_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/clients/", response_model=list[ClientRead], status_code=status.HTTP_200_OK)
async def list_clients(session: SessionDep):
    try:
        clients_list = await client_handler.get_clients_list(session)
        return clients_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@app.post("/vehicles/", response_model=VehicleRead, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    session: SessionDep,
    vehicle_data: VehicleCreate
):
    try:
        return save_vehicle_in_db(session, vehicle_data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))
    
@app.get("/vehicles/", response_model=VehicleRead, status_code=status.HTTP_200_OK)
async def search_vehicle(session: SessionDep, vehicle_code: str):
    try:
        vehicle_data = await vehicle_handler.get_vehicle_data(session, vehicle_code)
        return vehicle_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


    
    


    
    

