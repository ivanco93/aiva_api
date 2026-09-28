# AIVA API

**AI Video Analytics API**: backend en FastAPI para la gestión de cámaras y la analítica de video.

La arquitectura es **DDD + hexagonal**, organizada por módulos. Cada módulo separa `domain` (reglas de negocio), `application` (casos de uso) e `infrastructure` (HTTP y base de datos).

## Stack

- Python 3.14
- FastAPI + Uvicorn
- SQLAlchemy 2 (async) + aiomysql → MySQL 8.0.16+
- Pydantic / pydantic-settings
- Flyway (migraciones SQL)
- pytest + anyio

## Puesta en marcha

Desde `C:\Tools\aiva\aiva_api`:

```powershell
# 1. Entorno virtual y dependencias
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Variables de entorno
copy .env.example .env
#    editar DATABASE_URL, ej: mysql+aiomysql://usuario:password@127.0.0.1:3306/aiva

# 3. Base de datos
cd database\flyway
copy flyway.conf.example flyway.conf   # poner credenciales reales solo en flyway.conf
flyway migrate
cd ..\..

# 4. Levantar la API
uvicorn aiva.main:app --app-dir src --reload
```

- Documentación interactiva: http://127.0.0.1:8000/docs
- Healthcheck general: `GET /api/v1/health`

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
