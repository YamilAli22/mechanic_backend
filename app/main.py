from contextlib import asynccontextmanager
from typing import Optional, Annotated
from uuid import UUID
from handlers import client_handler, vehicle_handler, repair_handler, mechanic_handler
from sqlmodel import Session
from fastapi import FastAPI, HTTPException, Query, status, exceptions, Depends
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

# ============= MECHANICS =============

@app.post("/mechanic/", response_model=MechanicRead, status_code=status.HTTP_201_CREATED)
def create_mechanic(session: Annotated[Session, Depends(get_session)], mechanic_data: MechanicCreate):
    try:
        return save_mechanic_in_db(session, mechanic_data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))
    
@app.get("/mechanic/{mechanic_id}", response_model=MechanicRead, status_code=status.HTTP_200_OK)
async def search_mechanic_by_id(session: Annotated[Session, Depends(get_session)], mechanic_id: UUID):
    try:
        mechanic_data = await mechanic_handler.get_mechanic_data(session, mechanic_id)
        return mechanic_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/mechanic/", response_model=list[MechanicRead], status_code=status.HTTP_200_OK)
async def list_or_search_mechanics(
    session: Annotated[Session, Depends(get_session)], 
    q: Annotated[str | None, Query(min_length=2, description="Nombre del mecánico")] = None
):
    try:
        mechanic =  await mechanic_handler.search_mechanics(session, q)
        return mechanic
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al buscar mecánico")
    
# ============= CLIENTS =============

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

@app.get(
    "/clients/{client_id}", response_model=Optional[ClientRead], 
    status_code=status.HTTP_200_OK
)
async def search_client_by_id(session: Annotated[Session, Depends(get_session)], client_id: UUID):
    try:
        client_data = await client_handler.get_client_data(client_id, session)
        return client_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
       
@app.get("/clients/", response_model=list[ClientRead], status_code=status.HTTP_200_OK)
async def list_or_search_clients(
    session: Annotated[Session, Depends(get_session)],
    q: Annotated[str | None, Query(min_length=2, description="Nombre del cliente")] = None,
    limit: int = Query(20, le=100)
):
    try:
        clients = await client_handler.search_clients(session, q, limit)
        return clients
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Datos inválidos: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# ============= VEHICLES =============

@app.post("/vehicles/", response_model=VehicleRead, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    session: Annotated[Session, Depends(get_session)],
    vehicle_data: VehicleCreate
):
    try:
        return save_vehicle_in_db(session, vehicle_data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))

@app.get(
    "/vehicles/{vehicle_id}", response_model=VehicleRead, 
    status_code=status.HTTP_200_OK
)
async def search_vehicle_by_id(session: Annotated[Session, Depends(get_session)], vehicle_id: UUID):
    try:
        vehicles_list = await vehicle_handler.get_vehicle_data(session, vehicle_id)
        return vehicles_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get(
    "/vehicles/", response_model=list[VehicleRead], 
    status_code=status.HTTP_200_OK
)
async def search_or_list_vehicles(
    session: Annotated[Session, Depends(get_session)],
    q: Annotated[str | None, Query(min_length=2, description="Nombre del cliente")] = None,
    license_plate: Annotated[str | None, Query(min_length=3, description="Patente")] = None,
    limit: int = Query(20, le=100)
):
    try:
        vehicle_data = await vehicle_handler.search_vehicles(session, q, license_plate, limit)
        return vehicle_data
    except exceptions.ResponseValidationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# ============= REPAIRS =============
    
@app.post("/repairs/", response_model=RepairsRead, status_code=status.HTTP_201_CREATED)
def create_repair(session: Annotated[Session, Depends(get_session)], repair_data: RepairsCreate):
    try:
        return save_repair_in_db(session, repair_data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))
    
@app.get("/repairs/{repair_id}", response_model=RepairsRead, status_code=status.HTTP_200_OK)
async def search_repair_by_id(session: Annotated[Session, Depends(get_session)], repair_id: UUID):
    try:
        repair_data = await repair_handler.get_repair_data(session, repair_id)
        return repair_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/repairs/", response_model=list[RepairsRead], status_code=status.HTTP_200_OK)
async def search_or_list_repairs(
    session: Annotated[Session, Depends(get_session)],
    license_plate: Annotated[str | None, Query(min_length=3, description="Patente")] = None,
    client_name: Annotated[str | None, Query(min_length=2, description="Nombre del cliente")] = None,
    status: Annotated[RepairStatus | None, Query(description="Estado de la reparación")] = None,
    limit: int = Query(20, le=100)
):
    try:
        repairs = await repair_handler.search_repairs(session, license_plate, client_name, status, limit)
        return repairs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/repairs/{repair_id}", response_model=RepairsRead, status_code=status.HTTP_200_OK)
async def update_repair_info(session: Annotated[Session, Depends(get_session)], repair_id: UUID, update: RepairsUpdate):
    try:
        updated_data = await repair_handler.update_info(session, repair_id, update)
        return updated_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    

