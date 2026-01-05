from contextlib import asynccontextmanager
from typing import Optional, Annotated, cast
from uuid import UUID
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from fastapi import FastAPI, Depends, HTTPException, Query, status, exceptions
from decouple import config

from app.handlers import client_handler, vehicle_handler, repair_handler, mechanic_handler
from app.db import *
from app.schemas.client import *
from app.schemas.vehicle import *
from app.schemas.repairs import *
from app.schemas.mechanic import *
from app.auth.auth_handler import TokenResponse, get_current_mechanic, sign_jwt

# esto deberia ejecutarse antes de que la app empieze a recibir requests
# es decir, lo primero que quiero hacer es crear la base de datos
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

# endpoints

# ============= MECHANICS =============

@app.post("/mechanic/signup", tags=["Mechanics"], response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def create_mechanic(session: Annotated[Session, Depends(get_session)], mechanic_data: MechanicCreate):
    if mechanic_data.registration_code != cast(str, config("MECHANIC_REGISTRATION_CODE")):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid registration code"
        )
    mechanic = save_mechanic_in_db(session, mechanic_data)
    token = sign_jwt(mechanic)

    return {
        "access_token": token,
        "token_type": "bearer",
        "mechanic": mechanic
    }

@app.post("/mechanic/login", tags=["Mechanics"], response_model=TokenResponse, status_code=status.HTTP_202_ACCEPTED)
async def mechanic_login(session: Annotated[Session, Depends(get_session)], form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    mechanic = await mechanic_handler.check_mechanic(session, form_data.username, form_data.password)
    if not mechanic:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect Creds",
                            headers={"WWW-Authenticate": "Bearer"}) 
    token = sign_jwt(mechanic)

    return {
        "access_token": token,
        "token_type": "bearer",
        "mechanic": mechanic
    }

@app.get("/mechanic/me", tags=["Mechanics"], response_model=MechanicRead, status_code=status.HTTP_200_OK)
async def read_mechanics_me(current_mechanic: Annotated[Mechanic, Depends(get_current_mechanic)]):
    return current_mechanic

@app.get("/mechanic/{mechanic_id}", tags=["Mechanics"], response_model=MechanicRead, status_code=status.HTTP_200_OK)
async def search_mechanic_by_id(session: Annotated[Session, Depends(get_session)],
                                auth_mechanic: Annotated[Mechanic, Depends(get_current_mechanic)],
                                mechanic_id: UUID
):
    mechanic_data = await mechanic_handler.get_mechanic_data(session, mechanic_id)
    if not mechanic_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mechanic not found")

    return mechanic_data
    
@app.get("/mechanic/", tags=["Mechanics"], response_model=list[MechanicRead], status_code=status.HTTP_200_OK)
async def list_or_search_mechanics(
    session: Annotated[Session, Depends(get_session)],
    auth_mechanic: Annotated[Mechanic, Depends(get_current_mechanic)],
    q: Annotated[str | None, Query(min_length=2, description="Nombre del mecánico")] = None
):
    mechanic =  await mechanic_handler.search_mechanics(session, q)
    return mechanic

@app.patch("/mechanic/{mechanic_id}", tags=["Mechanics"], response_model=MechanicRead, status_code=status.HTTP_200_OK)
async def update_mechanic_data(
    session: Annotated[Session, Depends(get_session)],
    auth_mechanic: Annotated[Mechanic, Depends(get_current_mechanic)],
    mechanic_id: UUID,
    update: MechanicUpdate
):
    updated_mechanic = await mechanic_handler.update_mechanic(session, mechanic_id, update)
    return updated_mechanic

@app.delete("/mechanic/{mechanic_id}", tags=["Mechanics"], status_code=status.HTTP_204_NO_CONTENT)
async def soft_delete_mechanic(
    session: Annotated[Session, Depends(get_session)],
    auth_mechanic: Annotated[Mechanic, Depends(get_current_mechanic)],
    mechanic_id: UUID
):
    try:
        await mechanic_handler.delete_mechanic(session, mechanic_id) 
    except Exception:
        raise HTTPException(status_code=500, detail="Error borrando datos")

# ============= CLIENTS =============

@app.post("/clients/", tags=["Clients"], response_model=ClientRead, status_code=status.HTTP_201_CREATED)
def create_client(
    session: Annotated[Session, Depends(get_session)],
    auth_mechanic: Annotated[Mechanic, Depends(get_current_mechanic)],
    client_data: ClientCreate
):
    try:
        return save_client_in_db(client_data, session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))

@app.get(
    "/clients/{client_id}", tags=["Clients"], response_model=Optional[ClientRead], 
    status_code=status.HTTP_200_OK
)
async def search_client_by_id(session: Annotated[Session, Depends(get_session)], 
                              auth_mechanic: Annotated[Mechanic, Depends(get_current_mechanic)],
                              client_id: UUID
):
    try:
        client_data = await client_handler.get_client_data(client_id, session)
        return client_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
       
@app.get("/clients/", tags=["Clients"], response_model=list[ClientRead], status_code=status.HTTP_200_OK)
async def list_or_search_clients(
    session: Annotated[Session, Depends(get_session)],
    auth_mechanic: Annotated[Mechanic, Depends(get_current_mechanic)],
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

@app.patch("/clients/{client_id}", tags=["Clients"], response_model=ClientRead, status_code=status.HTTP_200_OK)
async def update_client_data(
    session: Annotated[Session, Depends(get_session)],
    auth_mechanic: Annotated[Mechanic, Depends(get_current_mechanic)],
    client_id: UUID,
    update: ClientUpdate 
):
    try:
        updated_client = await client_handler.update_client(session, client_id, update)
        return updated_client 
    except Exception:
        raise HTTPException(status_code=500, detail="Error en la actualización")

@app.delete("/client/{client_id}", tags=["Clients"], status_code=status.HTTP_204_NO_CONTENT)
async def soft_delete_client(
    session: Annotated[Session, Depends(get_session)],
    auth_mechanic: Annotated[Mechanic, Depends(get_current_mechanic)],
    client_id: UUID
):
    try:
        await client_handler.delete_client(session, client_id) 
    except Exception:
        raise HTTPException(status_code=500, detail="Error borrando datos")

# ============= VEHICLES =============

@app.post("/clients/{client_id}/vehicles/", tags=["Vehicles"], response_model=VehicleRead, status_code=status.HTTP_201_CREATED)
def create_vehicle_for_client(
    session: Annotated[Session, Depends(get_session)],
    auth_mechanic: Annotated[Mechanic, Depends(get_current_mechanic)],
    client_id: UUID,
    vehicle_data: VehicleCreate
):
    return save_vehicle_in_db(session, vehicle_data, client_id)

@app.get(
    "/vehicles/{vehicle_id}", tags=["Vehicles"], response_model=VehicleRead, 
    status_code=status.HTTP_200_OK
)
async def search_vehicle_by_id(session: Annotated[Session, Depends(get_session)], 
                               auth_mechanic: Annotated[Mechanic, Depends(get_current_mechanic)],
                               vehicle_id: UUID
):
    try:
        vehicles_list = await vehicle_handler.get_vehicle_data(session, vehicle_id)
        return vehicles_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get(
    "/vehicles/", tags=["Vehicles"], response_model=list[VehicleRead], 
    status_code=status.HTTP_200_OK
)
async def search_or_list_vehicles(
    session: Annotated[Session, Depends(get_session)],
    auth_mechanic: Annotated[Mechanic, Depends(get_current_mechanic)],
    q: Annotated[str | None, Query(min_length=2, description="Nombre del cliente")] = None,
    license_plate: Annotated[str | None, Query(min_length=3, description="Patente")] = None,
    limit: int = Query(20, le=100)
):
    try:
        vehicle_data = await vehicle_handler.search_vehicles(session, q, license_plate, limit)
        return vehicle_data
    except exceptions.ResponseValidationError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/clients/{client_id}/vehicles/", tags=["Vehicles"], response_model=list[VehicleRead], status_code=status.HTTP_200_OK)
async def get_vehicles_of_client(
    session: Annotated[Session, Depends(get_session)],
    auth_mechanic: Annotated[Mechanic, Depends(get_current_mechanic)],
    client_id: UUID
):
    vehicles_of_client = await vehicle_handler.get_client_vehicles(session, client_id)
    return vehicles_of_client

@app.patch("/vehicles/{vehicle_id}", tags=["Vehicles"], response_model=VehicleRead, status_code=status.HTTP_200_OK)
async def update_vehicle_data(
    session: Annotated[Session, Depends(get_session)],
    auth_mechanic: Annotated[Mechanic, Depends(get_current_mechanic)],
    vehicle_id: UUID,
    update: VehicleUpdate 
):
    try:
        updated_vehicle = await vehicle_handler.update_vehicle(session, vehicle_id, update)
        return updated_vehicle 
    except Exception:
        raise HTTPException(status_code=500, detail="Error en la actualización")


@app.delete("/vehicles/{vehicle_id}", tags=["Vehicles"], status_code=status.HTTP_204_NO_CONTENT)
async def soft_delete_vehicle(
    session: Annotated[Session, Depends(get_session)],
    auth_mechanic: Annotated[Mechanic, Depends(get_current_mechanic)],
    vehicle_id: UUID
):
    try:
        await vehicle_handler.delete_vehicle(session, vehicle_id) 
    except Exception:
        raise HTTPException(status_code=500, detail="Error borrando datos")

        
# ============= REPAIRS =============
    
@app.post("/vehicle/{mechanic_id}/{vehicle_id}/repairs/", tags=["Repairs"], response_model=RepairsRead, status_code=status.HTTP_201_CREATED)
def create_repair(session: Annotated[Session, Depends(get_session)], 
                  auth_mechanic: Annotated[Mechanic, Depends(get_current_mechanic)],
                  mechanic_id: UUID,
                  vehicle_id: UUID,
                  repair_data: RepairsCreate
):
    return save_repair_in_db(session, repair_data, mechanic_id, vehicle_id)
    
@app.get("/repairs/{repair_id}", tags=["Repairs"], response_model=RepairsRead, status_code=status.HTTP_200_OK)
async def search_repair_by_id(session: Annotated[Session, Depends(get_session)], 
                              auth_mechanic: Annotated[Mechanic, Depends(get_current_mechanic)],
                              repair_id: UUID
):
    try:
        repair_data = await repair_handler.get_repair_data(session, repair_id)
        return repair_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/repairs/", tags=["Repairs"], response_model=list[RepairsRead], status_code=status.HTTP_200_OK)
async def search_or_list_repairs(
    session: Annotated[Session, Depends(get_session)],
    auth_mechanic: Annotated[Mechanic, Depends(get_current_mechanic)],
    license_plate: Annotated[str | None, Query(min_length=3, description="License plate")] = None,
    client_name: Annotated[str | None, Query(min_length=2, description="Client name")] = None,
    status: Annotated[RepairStatus | None, Query(description="Repair status")] = None,
    limit: int = Query(20, le=100)
):
    try:
        repairs = await repair_handler.search_repairs(session, license_plate, client_name, status, limit)
        return repairs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vehicles/{vehicle_id}/repairs/", tags=["Repairs"], description="Get record of repairs from a vehicle",
         response_model=list[RepairsRead], status_code=status.HTTP_200_OK)
async def get_repairs_record(session: Annotated[Session, Depends(get_session)], 
                             auth_mechanic: Annotated[Mechanic, Depends(get_current_mechanic)],
                             vehicle_id: UUID
):
    vehicle_repairs = await repair_handler.get_record_of_repairs(session, vehicle_id)
    return vehicle_repairs

@app.get("/mechanics/{mechanic_id}/repairs/", tags=["Repairs"], description="Get repairs assigned to a mechanic",
         response_model=list[RepairsRead], status_code=status.HTTP_200_OK)
async def get_repairs_mechanic(session: Annotated[Session, Depends(get_session)], 
                             auth_mechanic: Annotated[Mechanic, Depends(get_current_mechanic)],
                             mechanic_id: UUID
):
    mechanic_repairs = await repair_handler.get_mechanic_repairs(session, mechanic_id)
    return mechanic_repairs


@app.patch("/repairs/{repair_id}", tags=["Repairs"], response_model=RepairsRead, status_code=status.HTTP_200_OK)
async def update_repair_info(session: Annotated[Session, Depends(get_session)], 
                             auth_mechanic: Annotated[Mechanic, Depends(get_current_mechanic)],
                             repair_id: UUID, 
                             update: RepairsUpdate
):
    try:
        updated_data = await repair_handler.update_info(session, repair_id, update)
        return updated_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
@app.delete("/repairs/{repair_id}", tags=["Repairs"], status_code=status.HTTP_204_NO_CONTENT)
async def soft_delete_repair(
    session: Annotated[Session, Depends(get_session)],
    auth_mechanic: Annotated[Mechanic, Depends(get_current_mechanic)],
    repair_id: UUID
):
    try:
        await repair_handler.delete_repair(session, repair_id) 
    except Exception:
        raise HTTPException(status_code=500, detail="Error borrando datos")     
