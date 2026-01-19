# API de un Sistema de Gestión de Taller Mecánico

Sistema de gestión para talleres mecánicos con autenticación JWT y manejo completo de operaciones para mecánicos, clientes, vehículos y reparaciones

---
## 🚀 Features principales 

- ✅ Autenticación JWT para mecánicos
- ✅ CRUD completo: Mecánicos, Clientes, Vehículos, Reparaciones
- ✅ Gestión de estados de reparación
- ✅ Historial de reparaciones por vehículo
- ✅ Soft delete en todas las entidades
- ✅ Documentación interactiva (Swagger)

---

## 🛠️ Tech Stack

- **FastAPI** - Framework web moderno y rápido para Python
- **SQLModel** - ORM basado en Pydantic y SQLAlchemy
- **SQLite** - Base de datos (futura migración a PostgreSQL)
- **JWT** - Autenticación con tokens
- **Bcrypt** - Hash de contraseñas

---

## ⚙️ Instalación y ejecución

```bash 
# Clonar repo
git clone https://github.com/tu-usuario/taller-api.git
cd taller-api

# Crear y activar entorno virtual 
python3 -m venv ./venv
source .venv/bin/activate # Linux/Mac
# venv\Scripts\activate # Windows

# Instalar dependencias
pip3 install -r requirements.txt

# Configurar variables de entorno (ver sección Configuración)
cp .env.example .env # Editar con tus valores

```

---

## 🔧 Configuración

Crear un archivo `.env` en la raíz del proyecto con las siguientes variables:
```bash
# Clave secreta para JWT (genera una aleatoria con: python -c "import secrets; print(secrets.token_urlsafe(32))")
secret=tu_clave_secreta_super_larga_aqui

# Algoritmo de encriptación JWT
algorithm=HS256

# URL de la base de datos
DATABASE_URL=sqlite:///database.db

# Código de registro para mecánicos (cámbialo por uno propio)
MECHANIC_REGISTRATION_CODE=TU_CODIGO_AQUI
```

### Generar clave secreta segura
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copia el resultado y úsalo como valor de `secret` en tu `.env`.

---

## 🚀 Uso 
```bash
# Ejecutar el servidor
python3 main.py 

# O con uvicorn 
uvicorn app.api:app --reload
```

La API se encuentra disponible en `http://localhost:8000`

---

## 📚 Documentación

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔑 Autenticación

### Registro de mecánico 
```bash
curl -X POST "http://localhost:8000/mechanic/signup" \ 
    - H "Content-Type: application/json" \ 
    -d '{
        "name": "Juan Pérez",
        "email": juan@taller.com",
        "password": "password123",
        "phone": "123456789",
        "registration_code": "secret_code"
    }'
```
### Login
```bash
curl -X POST "http://localhost:8000/mechanic/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=juan@taller.com&password=contraseña123"
```

Respuesta:
```json
{
    "access_token":"eyJhbGciOiJIUzI1NiIsInR...",
    "token_type":"bearer",
    "mechanic": {"id":"...","email":"...","name":"...","phone":"..."}
}
```

### Usar el token
```bash
curl -X GET "http://localhost:8000/mechanic/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 📊 Ejemplos de uso

### Crear cliente
```bash
curl -X POST "http://localhost:8000/client/" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Carlos López",
    "phone_number": "987654321",
    "email": "carlos@email.com"
  }'
```

### Crear vehículo
```bash
curl -X POST "http://localhost:8000/vehicles" \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "license_plate": "ABC123",
    "brand": "Toyota",
    "model": "Corolla",
    "year": 2020,
    "client_id": "CLIENT_UUID"
  }'
```

### Ver historial de reparaciones
```bash
curl -X GET "http://localhost:8000/vehicles/{vehicle_id}/repairs" \
  -H "Authorization: Bearer TOKEN"
```

---

## 🏗️ Arquitectura
```
taller/
├── app/
│   ├── api.py              # Endpoints principales
│   ├── db.py               # Configuración de base de datos
│   ├── models.py           # Modelos SQLModel
│   ├── auth/
│   │   ├── auth_handler.py # JWT encoding/decoding
│   │   ├── security.py     # Hashing de contraseñas
│   │
│   ├── handlers/           # Lógica de negocio
│   └── schemas/            # Pydantic schemas
├── main.py                 # Entry point
├── .env                    # Variables de entorno
└── requirements.txt
```

---

## 🔐 Seguridad

- Contraseñas hasheadas con bcrypt
- Autenticación JWT con expiración (15 min)
- Registro protegido con código de invitación
- Soft delete para preservar integridad referencial

---

## 🧪 Tests
```bash
pytest
```

---

## 🚀 Deploy

[Instrucciones de deploy - agregar después]

---

### Notas

- Usamos SQLModel, que funciona junto con Pydantic y SQLAlchemy, para crear modelos (clases) que representan las tablas y relaciones que se crearan en la base de datos.
- Y utilizamos modelos Pydantic para validar los datos que recibe y devuelve la API y que estos se adapten correctamente a los modelos que definimos con SQLModel.
