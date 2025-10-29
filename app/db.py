from sqlmodel import Session, SQLModel, create_engine
from fastapi import HTTPException, status
from schemas.client import ClientCreate
from models import Mechanic, Client, Vehicle, Repairs, Record

sql_filename = "database.db"
sql_url = f"sqlite:///{sql_filename}"

connect_args = {"check_same_thread": False}
engine = create_engine(sql_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

def save_client_in_db(client_data: ClientCreate, session: Session) -> Client:
    client = Client(
                    name=client_data.name,
                    phone_number=client_data.phone_number,
                    email=client_data.email
                    )
    session.add(client)
    session.commit()
    session.refresh(client)
    return client



