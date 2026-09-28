# CLAUDE.md

Guía para Claude Code al trabajar en este repositorio.

## Comandos

Ejecutar desde `aiva_api` con el `.venv` activo.

```powershell
pip install -r requirements.txt                                   # dependencias
docker compose up -d                                              # PostgreSQL (5432) + pgAdmin (http://localhost:5050)
uvicorn aiva.main:app --app-dir src --reload                      # levantar la API (NO usar src.aiva.main:app)
$env:PYTHONPATH="src"; python -m pytest src/aiva/modules          # todos los tests
$env:PYTHONPATH="src"; python -m pytest src/aiva/modules/camera/tests   # tests de un módulo
cd database\flyway; flyway migrate                                # aplicar migraciones
```

- Tras instalar un paquete nuevo, añadirlo a `requirements.txt` (`pip freeze`).
- El usuario prefiere levantar uvicorn él mismo. Pregunta antes de arrancar servidores o ejecutar procesos largos.

## Arquitectura

DDD + hexagonal por módulos. Documentación completa en `docs/ARCHITECTURE-FLOW.md`. Antes de crear o modificar un módulo, léela y sigue su checklist (sección 7).

```
src/aiva/
├── main.py              # crea la app y llama a {module}.module.register(app)
├── config/settings.py   # pydantic-settings; DATABASE_URL obligatoria
├── database/            # Base común, engine/get_session, SqlAlchemyTransactionManager
├── testing/             # TransactionManagerStub y otros dobles genéricos
└── modules/{module}/
    ├── module.py        # ≈ ServiceProvider: include_router(prefix="/api/v1") + exception handlers
    ├── domain/          # entities, value_objects, enums, exceptions, repositories (Protocol)
    ├── application/     # contracts, dto, builders, use_cases/{entity}/
    ├── infrastructure/  # http (routers, schemas, dependencies, exception_handlers) + persistence/sqlalchemy
    └── tests/           # conftest, fakes (repos en memoria), unit/
```

### Flujo de una petición

```
router → schema Pydantic → builder (dict → DTO) → UseCase.execute(dto)
  → entidad/VO (reglas) → async with transaction_manager.transaction(): repo.find/save
  → ResponseBuilder (entidad → DTO) → schema de respuesta → JSON
```

Las dependencias se arman en `infrastructure/http/dependencies.py`. FastAPI cachea `get_session` por request, así que el repositorio y el transaction manager comparten la misma sesión.

## Reglas obligatorias

- **No crear `shared/`, `common/`, `core/` ni ningún paquete comodín.** El usuario lo rechazó explícitamente para evitar un God module. Lo técnico común va en paquetes con propósito único (`aiva/database/`, `aiva/testing/`). Si hace falta algo nuevo, se crea otro paquete con nombre propio (ej. `aiva/cache/`). Estos paquetes no importan nada de `modules/`.
- **Capas:**
  - `domain` no importa FastAPI, SQLAlchemy, Pydantic ni otras capas o módulos.
  - `application` solo importa `domain`.
  - `infrastructure` puede importar todo.
- **Los puertos viven en el módulo que los consume:**
  - `domain/repositories/` para la persistencia.
  - `application/contracts/` para el resto (ej. `TransactionManager`).
  - Son `Protocol`: las implementaciones de `aiva/database/` los cumplen por tipado estructural.
- **Sin try/except** en routers, casos de uso ni repositorios. Las excepciones de dominio heredan de `{Module}Error` y las traduce a HTTP `infrastructure/http/exception_handlers.py`, registrado en `module.py`.
- **Routers delgados:** schema → builder → caso de uso → `Response.model_validate(dto)`, sin lógica.
- **Builders en `application/`** reciben `Mapping[str, Any]` (`body.model_dump()`), nunca schemas Pydantic.
- **DTOs:** `@dataclass(frozen=True, slots=True)`.
- **Entidades:** validan todo antes de asignar, para no quedar a medio modificar.
- **Modelos SQLAlchemy** heredan de `aiva.database.base.Base`. El esquema lo gestiona **Flyway**, no SQLAlchemy ni Alembic.
- **Los repositorios en memoria** de los tests devuelven copias (`dataclasses.replace`).

## Convenciones

- **Rutas:**
  - `POST /{recurso}` crea.
  - `GET /{recurso}` lista (filtros opcionales en query params: `Annotated[{Schema}, Query()]`).
  - `GET /{recurso}/{id:int}` consulta uno.
  - `PUT /{recurso}/{id:int}` actualiza.
  - `PUT /{recurso}/{id:int}/status` cambia el estado.
  - `DELETE /{recurso}/{id:int}` borra (responde 204).
  - Usar siempre `:int` en los path params numéricos, para que no choquen con rutas fijas.
- **Respuestas:**
  - Listados: `{ "data": [...], "count": N }`, con paginación `offset`/`limit`.
  - Errores: `{ "detail": "..." }`.
- **Nombres:**
  - Casos de uso: `{Accion}{Entity}UseCase` en `use_cases/{entity}/{accion}_{entity}.py`.
  - Repositorio real: `SqlAlchemy{Entity}Repository`.
  - Excepciones: `*Error`.
- **Migraciones:** `database/flyway/{module}/V{yyMMddHHmmss}__descripcion.sql`, sin `BEGIN`/`COMMIT` (Flyway ya envuelve cada migración en una transacción en PostgreSQL). Cada módulo nuevo se añade a `flyway.locations`.
- **Idioma:** los mensajes de error y los comentarios van en español.
- **Estilo:** cada carpeta de paquete lleva su `__init__.py` vacío.

## Documentación

- `docs/ARCHITECTURE-FLOW.md`: guía general para cualquier módulo.
- `docs/{MODULE}-MODULE.md`: un documento por módulo (ej. `docs/CAMERA-MODULE.md`). Actualizarlo al cambiar un módulo.

## Pendientes conocidos

- `camera`:
  - Si dos requests crean el mismo `code` a la vez, se responde 500 en lugar de 409 (falta mapear `IntegrityError`).
  - `location_id` no tiene FK.
  - `source_url` puede contener credenciales.
- No hay autenticación, autorización, auditoría (`created_by`/`updated_by`) ni multi-tenant.
- No hay `pyproject.toml`, ni configuración de ruff/mypy/import-linter.
- Las credenciales reales van solo en `.env` (también las lee `docker-compose.yml`) y `database/flyway/flyway.conf` (ignorados por git). Los `.example` llevan marcadores. El repositorio es público.
