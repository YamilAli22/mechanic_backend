# Sistema de Gestión de Taller Mecánico

Aplicación web para registrar vehiculos, clientes y reparaciones, llevar un registro de los mismos y permitir al cliente realizar un seguimiento sobre el estado de su vehiculo.

---

## Stack tecnológico:
- **Python 3.12**
- **FastAPI**
- **SQL**

---

## Instalación y ejecución

- Primero dirigirse a la carpeta donde se encuentra el proyecto y crear un entorno virtual:
  ```bash
  cd backend/app
  python3 -m venv ./venv
  source .venv/bin/activate
  ```
- Luego instalar las dependencias:
  ```bash
  pip3 install -r requirements.txt
  ```
- Levantar el servidor ubicado en taller/app:
  ```bash
  fastapi dev main.py
  ```
- También puede levantar el servidor recargable:
  ```bash
  uvicorn main:app --reload
  ```
- Puede probar la API en la documentacion de FastAPI con Swagger en *http://127.0.0.1:8000/docs*

---

### Notas

- Usamos SQLModel, que funciona junto con Pydantic y SQLAlchemy, para crear modelos (clases) que representan las tablas y relaciones que se crearan en la base de datos.
- Y utilizamos modelos Pydantic para validar los datos que recibe y devuelve la API y que estos se adapten correctamente a los modelos que definimos con SQLModel.

Ejemplo:

```python

# MODELO PYDANTIC:

from pydantic import BaseModel, EmailStr
from uuid import UUID

class ClientCreate(BaseModel):
    name: str
    phone_number: str
    email: EmailStr

class ClientRead(BaseModel):
    id: UUID
    name: str
    phone_number: str
    email: EmailStr

    class Config:
        from_attributes = True

# OBJETO SQLMODEL:

class Client(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    phone_number: str = Field(index=True)
    email: EmailStr = Field(index=True, max_length=255)

    vehicles: List["Vehicle"] = Relationship(back_populates="clients")
```

Lo primero que vemos en el código de arriba, es un modelo pydantic que será utilizado por la API
al recibir y devolver datos, y luego nuestro modelo SQL que representa la tabla que se creara 
en la base de datos. La clase ```Config``` sirve para que FastAPI convierta un objeto SQLModel
en un JSON, por ejemplo, cuando queremos devolver los datos del cliente luego de crearlo con un 
POST request.