from contextlib import asynccontextmanager
from typing import Optional
from uuid import UUID
from handlers import client_handler, vehicle_handler, repair_handler, mechanic_handler

from fastapi import FastAPI, HTTPException, status
from db import *
from schemas.client import *
from schemas.vehicle import *
from schemas.repairs import *
from schemas.mechanic import *

# esto deberia ejecutarse antes de que la app empieze a recibir requests
# es decir, lo primero que quiero hacer es crear la base de datos
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield # deberia ir algo luego de este yield?

app = FastAPI(lifespan=lifespan)

# endpoints

@app.post("/mechanic/", response_model=MechanicRead, status_code=status.HTTP_201_CREATED)
def create_mechanic(session: SessionDep, mechanic_data: MechanicCreate):
    try:
        return save_mechanic_in_db(session, mechanic_data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))
    

@app.get("/mechanic/{mechanic_id}", response_model=MechanicRead, status_code=status.HTTP_200_OK)
async def search_mechanic(session: SessionDep, mechanic_id: UUID):
    try:
        mechanic_data = await mechanic_handler.get_mechanic_data(session, mechanic_id)
        return mechanic_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

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

    
@app.get(
    "/clients/{client_id}", response_model=Optional[ClientRead], 
    status_code=status.HTTP_200_OK
)
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


@app.get(
    "/clients/{client_id}/vehicles/", response_model=list[VehicleRead], 
    status_code=status.HTTP_200_OK
)
async def search_client_vehicles(session: SessionDep, client_id: UUID):
    try:
        vehicles_list = await vehicle_handler.get_client_vehicles(session, client_id)
        return vehicles_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get(
    "/clients/{client_id}/vehicles/{license_plate}", response_model=VehicleRead, 
    status_code=status.HTTP_200_OK
)
async def search_vehicle_by_code(session: SessionDep, client_id: UUID, license_plate: str):
    try:
        vehicle_data = await vehicle_handler.get_vehicle_data(session, client_id, license_plate)
        return vehicle_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@app.post("/vehicles/repairs/", response_model=RepairsRead, status_code=status.HTTP_201_CREATED)
def create_repair(session: SessionDep, repair_data: RepairsCreate):
    try:
        return save_repair_in_db(session, repair_data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))
    
    
@app.get("/vehicles/repairs/{repair_id}", response_model=RepairsRead, status_code=status.HTTP_200_OK)
async def search_for_repair(session: SessionDep, repair_id: UUID):
    try:
        repair_data = await repair_handler.get_repair_data(session, repair_id)
        return repair_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
@app.patch("/vehicles/repairs/{repair_id}", response_model=RepairsRead, status_code=status.HTTP_200_OK)
async def update_repair_info(session: SessionDep, repair_id: UUID, status: RepairStatus, info: RepairsCreate):
    try:
        updated_data = await repair_handler.update_info(session, repair_id, status, info)
        return updated_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

