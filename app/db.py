from pydantic import EmailStr
from fastapi import HTTPException, status
from sqlmodel import Field, Session, SQLModel, create_engine
from uuid import UUID, uuid4
from datetime import datetime
from capsule_handler import MessageMeta, ContentType

class Capsule(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    sender_id: UUID = Field(default_factory=uuid4)
    content: str = Field(index=True) # texto o ruta de archivo (para imagenes por ej)
    content_type: ContentType = Field(default=ContentType.text, index=True) # type = texto o url de archivo
    email: EmailStr = Field(index=True, max_length=255)
    created_at: datetime = Field(default_factory=datetime.now, index=True)
    unlock_date: datetime = Field(index=True)

sql_filename = "database.db"
sql_url = f"sqlite:///{sql_filename}"

connect_args = {"check_same_thread": False}
engine = create_engine(sql_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

def save_capsule_in_db(msg_metadata: MessageMeta, msg_content: str, session: Session):
    try:
        capsule = Capsule(
            content=msg_content,
            content_type=msg_metadata.content_type,
            email=msg_metadata.email,
            unlock_date=msg_metadata.unlock_date
        )
        session.add(capsule)
        session.commit()
        session.refresh(capsule)
        return capsule
    except Exception as e:
        print("ERROR:", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=str(e))
