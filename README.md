# AIVA API

**AI Video Analytics API**: backend en FastAPI para la gestión de cámaras y la analítica de video.

La arquitectura es **DDD + hexagonal**, organizada por módulos. Cada módulo separa `domain` (reglas de negocio), `application` (casos de uso) e `infrastructure` (HTTP y base de datos).

## Stack

- Python 3.14
- FastAPI + Uvicorn
- SQLAlchemy 2 (async) + asyncpg → PostgreSQL 17 (Docker Compose, con pgAdmin)
- Pydantic / pydantic-settings
- Flyway (migraciones SQL)
- pytest + anyio

## Puesta en marcha

Desde raíz del proyecto:

```powershell
# 1. Entorno virtual y dependencias
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Variables de entorno
copy .env.example .env
#    poner usuario/contraseñas; DATABASE_URL debe coincidir con POSTGRES_*:
#    postgresql+asyncpg://usuario:password@127.0.0.1:5432/aiva

# 3. Base de datos (PostgreSQL + pgAdmin en Docker; lee las credenciales del .env)
docker compose up -d
cd database\flyway
copy flyway.conf.example flyway.conf   # poner credenciales reales solo en flyway.conf
flyway migrate
cd ..\..

# 4. Levantar la API
uvicorn aiva.main:app --app-dir src --reload
```

- Documentación interactiva: http://127.0.0.1:8000/docs
- Healthcheck general: `GET /api/v1/health`
- pgAdmin: http://localhost:5050 (modo escritorio, sin pantalla de login). El servidor "AIVA" ya aparece registrado; pide la contraseña de `POSTGRES_PASSWORD` la primera vez.

`--app-dir src` es necesario porque el paquete `aiva` vive dentro de `src/`. La ruta de la app es `aiva.main:app`, no `src.aiva.main:app`.

## Tests

```powershell
$env:PYTHONPATH="src"; python -m pytest src/aiva/modules/camera/tests
```

Los tests unitarios no necesitan base de datos: usan repositorios en memoria y un stub de transacciones.

## Estructura

```
aiva_api/
├── database/flyway/{module}/     # migraciones SQL por módulo
├── docs/                         # documentación de arquitectura y módulos
└── src/aiva/
    ├── main.py                   # app FastAPI + registro de módulos
    ├── config/                   # settings (.env)
    ├── database/                 # Base, sesión y transaction manager comunes
    ├── testing/                  # dobles de prueba genéricos
    └── modules/
        └── camera/
            ├── module.py         # registra routers y exception handlers
            ├── domain/
            ├── application/
            ├── infrastructure/
            └── tests/
```

## Módulos

| Módulo | Endpoints | Documentación |
|---|---|---|
| `camera` | CRUD de cámaras en `/api/v1/cameras` | [docs/CAMERA-MODULE.md](docs/CAMERA-MODULE.md) |

## Documentación

- [docs/ARCHITECTURE-FLOW.md](docs/ARCHITECTURE-FLOW.md): capas, flujo de una petición, manejo de errores y checklist para crear un módulo nuevo.
- [docs/CAMERA-MODULE.md](docs/CAMERA-MODULE.md): tabla, endpoints y archivos del módulo `camera`.
