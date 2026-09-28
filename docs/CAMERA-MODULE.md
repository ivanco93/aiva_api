# Módulo `camera`

Documentación específica del módulo `camera`: endpoints, archivos que lo componen y el recorrido concreto de una petición.

Para las reglas generales de arquitectura (capas, flujo genérico, checklist de módulo nuevo), ver [ARCHITECTURE-FLOW.md](ARCHITECTURE-FLOW.md).

---

## 1. Tabla `cameras`

Migración: `database/flyway/camera/V260927120001__create_cameras.sql` (PostgreSQL 17).

| Columna | Tipo | Detalle |
|---|---|---|
| `id` | `INTEGER GENERATED ALWAYS AS IDENTITY` | PK |
| `name` | `VARCHAR(100)` | Obligatorio; el filtro del listado usa `ILIKE` (no distingue mayúsculas) |
| `code` | `VARCHAR(30)` | Único sin distinguir mayúsculas: índice `uq_cameras_code` sobre `lower(code)` (ej. `CAM-001`) |
| `location_id` | `INTEGER` + `CHECK (>= 0)` | Indexado; sin FK hasta que exista `locations` |
| `source_type` | `VARCHAR(20)` + `CHECK` | `rtsp`, `rtmp`, `http`, `hls` o `file` |
| `source_url` | `VARCHAR(2048)` | URL o ruta de la fuente |
| `status` | `VARCHAR(20)` + `CHECK` | `active` (por defecto), `inactive` o `maintenance` |
| `created_at` | `TIMESTAMPTZ` | `DEFAULT now()` |
| `updated_at` | `TIMESTAMPTZ NULL` | La fija el trigger `trg_cameras_updated_at` (función `set_updated_at()`) en cada `UPDATE` que cambie la fila |

---

## 2. Endpoints (`/api/v1/cameras`)

| Método | Ruta | Acción | Respuesta |
|---|---|---|---|
| POST | `/cameras` | Crear | 201 + cámara |
| GET | `/cameras` | Listar con filtros en query params | `{ "data": [...], "count": N }` |
| GET | `/cameras/{id}` | Ver una | cámara |
| PUT | `/cameras/{id}` | Actualizar | cámara |
| PUT | `/cameras/{id}/status` | Cambiar estado | cámara |
| DELETE | `/cameras/{id}` | Eliminar (borrado físico) | 204 |

Filtros de `GET /cameras` (todos opcionales; solo se envían los que se usan, ej. `/api/v1/cameras?code=CAM-001&status=active`):
- `name`: búsqueda parcial, sin distinguir mayúsculas.
- `code`: coincidencia exacta, sin distinguir mayúsculas.
- `location_id`, `status`, `source_type`: coincidencia exacta.
- Paginación: `offset` (≥ 0, por defecto 0) y `limit` (1–100, por defecto 20).
- Un parámetro desconocido responde 422 (`extra="forbid"`).

Respuesta de una cámara:

```json
{
  "id": 1,
  "name": "Entrada principal",
  "code": "CAM-001",
  "location_id": 1,
  "source_type": "rtsp",
  "source_url": "rtsp://10.0.0.10:554/stream1",
  "status": "active",
  "created_at": "2026-09-27T12:00:00",
  "updated_at": null
}
```

Errores de dominio (`{ "detail": "..." }`):

| Excepción | HTTP | Cuándo |
|---|---|---|
| `CameraNotFoundError` | 404 | El id no existe |
| `CameraCodeAlreadyExistsError` | 409 | El `code` ya lo usa otra cámara |
| `InvalidCameraError` | 422 | Nombre o código vacío o demasiado largo, `location_id` ≤ 0, o una URL que no corresponde al `source_type` |

Reglas de `source_url` según `source_type`:

| `source_type` | Debe empezar por |
|---|---|
| `rtsp` | `rtsp://` o `rtsps://` |
| `rtmp` | `rtmp://` o `rtmps://` |
| `http` | `http://` o `https://` |
| `hls` | `http://` o `https://` |
| `file` | Sin restricción (acepta rutas locales) |

---

## 3. Archivos y qué hace cada uno

Los `__init__.py` vacíos solo marcan cada carpeta como paquete de Python y no se listan.

### Raíz del proyecto

| Archivo | Qué hace |
|---|---|
| `.env.example` | Plantilla de variables de entorno (`DATABASE_URL`, `DATABASE_ECHO`). Se copia como `.env` |
| `database/flyway/flyway.conf.example` | Configuración de Flyway: conexión y `locations=./camera` |
| `database/flyway/camera/V260927120001__create_cameras.sql` | Crea la tabla `cameras` con sus índices y los `CHECK` |

### Nivel de la app (`src/aiva/`)

| Archivo | Qué hace |
|---|---|
| `main.py` | Crea la app FastAPI, llama a `camera_module.register(app)` y cierra el pool de conexiones al apagar (`lifespan`) |
| `config/settings.py` | Lee `.env` con pydantic-settings. `database_url` es obligatoria |
| `database/base.py` | `Base` (DeclarativeBase) común a los modelos de todos los módulos |
| `database/session.py` | Crea el `engine`, la `SessionFactory` y `get_session()`, que abre una sesión por request |
| `database/sqlalchemy_transaction_manager.py` | Implementación real del `TransactionManager`: commit si todo sale bien, rollback si hay excepción |
| `testing/transaction_manager_stub.py` | `TransactionManager` falso para tests: no toca la BD y cuenta los commits y rollbacks |

### Registro del módulo

| Archivo | Qué hace |
|---|---|
| `modules/camera/module.py` | Equivale al `ServiceProvider`: registra el router de cámaras y los handlers de errores |

### `domain/` (reglas de negocio, sin frameworks)

| Archivo | Qué hace |
|---|---|
| `entities/camera.py` | Entidad `Camera` con `create()`, `update()` y `change_status()`. Valida el nombre, el código y el `location_id`, y no se deja a medio modificar si una validación falla |
| `value_objects/camera_source.py` | `CameraSource` (tipo + URL), inmutable. Exige que la URL corresponda al tipo |
| `enums/camera_status.py` | `active`, `inactive`, `maintenance` |
| `enums/camera_source_type.py` | `rtsp`, `rtmp`, `http`, `hls`, `file` |
| `exceptions/camera_error.py` | Excepción base del módulo; el handler HTTP captura esta |
| `exceptions/camera_not_found_error.py` | La cámara no existe (404) |
| `exceptions/camera_code_already_exists_error.py` | El código está repetido (409) |
| `exceptions/invalid_camera_error.py` | Se rompe una regla de negocio (422) |
| `repositories/camera_repository.py` | Puerto (`Protocol`): `find_by_id`, `find_by_code`, `search`, `save` y `delete` |

### `application/` (orquestación)

| Archivo | Qué hace |
|---|---|
| `contracts/transaction_manager.py` | Puerto `TransactionManager`: lo que el caso de uso espera para manejar transacciones |
| `dto/create_camera_dto.py` | Datos de entrada para crear |
| `dto/update_camera_dto.py` | Datos de entrada para actualizar (incluye `camera_id`) |
| `dto/change_camera_status_dto.py` | Datos de entrada para cambiar el estado |
| `dto/list_cameras_query_dto.py` | Filtros y paginación del listado |
| `dto/response/camera_response_dto.py` | Salida de una cámara |
| `dto/response/camera_list_response_dto.py` | Salida del listado: `data` + `count` |
| `builders/create_camera_builder.py` | Convierte un dict en `CreateCameraDTO` |
| `builders/update_camera_builder.py` | Convierte `camera_id` + dict en `UpdateCameraDTO` |
| `builders/change_camera_status_builder.py` | Convierte `camera_id` + dict en `ChangeCameraStatusDTO` |
| `builders/list_cameras_query_builder.py` | Convierte un dict en `ListCamerasQueryDTO`: pasa los vacíos a `None` y pone valores por defecto |
| `builders/response/camera_response_builder.py` | Convierte la entidad `Camera` en `CameraResponseDTO`, y una lista en `CameraListResponseDTO` |
| `use_cases/camera/create_camera.py` | Crea la entidad, verifica que el código sea único y guarda |
| `use_cases/camera/show_camera_by_id.py` | Busca por id; si no existe, lanza 404 |
| `use_cases/camera/list_cameras.py` | Busca con filtros y paginación |
| `use_cases/camera/update_camera.py` | Busca la cámara, llama a `update()`, verifica que el código siga siendo único y guarda |
| `use_cases/camera/change_camera_status.py` | Busca la cámara, llama a `change_status()` y guarda |
| `use_cases/camera/delete_camera.py` | Verifica que exista y la borra |

### `infrastructure/` (adaptadores)

| Archivo | Qué hace |
|---|---|
| `http/routers/camera_router.py` | Los 6 endpoints del CRUD. Son funciones delgadas: schema → builder → caso de uso → respuesta |
| `http/schemas/concerns/camera_fields.py` | Campos comunes con sus validaciones de tipo y longitud; los reutilizan crear y actualizar |
| `http/schemas/create_camera_request.py` | Body del POST de creación |
| `http/schemas/update_camera_request.py` | Body del PUT |
| `http/schemas/change_camera_status_request.py` | Body del PUT de estado |
| `http/schemas/list_cameras_request.py` | Query params de `GET /cameras` (se recibe con `Annotated[ListCamerasRequest, Query()]`) |
| `http/schemas/camera_response.py` | Forma del JSON de salida (`CameraResponse`, `CameraListResponse`); también aparece documentada en `/docs` |
| `http/dependencies.py` | Arma las piezas: sesión → repositorio + transaction manager → caso de uso |
| `http/exception_handlers.py` | Traduce las excepciones de dominio a HTTP (404, 409 o 422) con `{"detail": ...}` |
| `persistence/sqlalchemy/models/camera_model.py` | Modelo SQLAlchemy de la tabla `cameras` (hereda de `aiva.database.base.Base`) |
| `persistence/sqlalchemy/mappers/camera_mapper.py` | Traduce en ambos sentidos entre el modelo y la entidad |
| `persistence/sqlalchemy/repositories/sqlalchemy_camera_repository.py` | Implementa `CameraRepository` con SQLAlchemy |

### `tests/`

| Archivo | Qué hace |
|---|---|
| `conftest.py` | Configura `anyio` para que los tests async corran con asyncio |
| `fakes.py` | `InMemoryCameraRepository`: repositorio en memoria que devuelve copias |
| `unit/domain/test_camera.py` | Tests de la entidad: creación, validaciones, que `update` no deje la entidad a medias, cambio de estado |
| `unit/domain/test_camera_source.py` | Tests del value object: esquemas válidos e inválidos, URL vacía, `file` |
| `unit/use_cases/test_camera_use_cases.py` | Tests de los 6 casos de uso, incluidos el código duplicado y el rollback |

---

## 4. Recorrido concreto: `POST /api/v1/cameras`

```
Cliente
  │  POST /api/v1/cameras   { "name": "Entrada", "code": "CAM-001", "location_id": 1,
  │                           "source_type": "rtsp", "source_url": "rtsp://10.0.0.10/stream1" }
  ▼
main.py ── la app tiene el router registrado por modules/camera/module.py
  ▼
camera_router.py → create_camera(body, use_case)
  │
  ├─① FastAPI valida el body con  schemas/create_camera_request.py  (hereda de concerns/camera_fields.py)
  │     ✗ tipo, longitud o source_type inválido → 422 automático
  │
  ├─② FastAPI resuelve Depends(get_create_camera_use_case)   http/dependencies.py
  │       get_session()                    aiva/database/session.py     (abre AsyncSession)
  │         ├─ get_camera_repository()     → SqlAlchemyCameraRepository(session)
  │         └─ get_transaction_manager()   → SqlAlchemyTransactionManager(session)
  │       → CreateCameraUseCase(repository, transaction_manager)
  │
  ├─③ CreateCameraBuilder.build(body.model_dump())   builders/create_camera_builder.py
  │       dict → CreateCameraDTO                       dto/create_camera_dto.py
  │
  └─④ use_case.execute(dto)                           use_cases/camera/create_camera.py
        │
        ├─ CameraSource(type, url)                   domain/value_objects/camera_source.py
        │     ✗ URL no coincide con el tipo → InvalidCameraError
        ├─ Camera.create(...)                        domain/entities/camera.py
        │     ✗ nombre vacío, etc. → InvalidCameraError
        │
        ├─ async with transaction_manager.transaction():   aiva/database/sqlalchemy_transaction_manager.py
        │     ├─ repository.find_by_code("CAM-001")
        │     │     sqlalchemy_camera_repository.py → SELECT … → camera_mapper.to_entity()
        │     │     ✗ existe → CameraCodeAlreadyExistsError  (→ rollback)
        │     └─ repository.save(camera)
        │           camera_mapper.apply_to_model()  → camera_model.py
        │           session.flush()   → INSERT INTO cameras …
        │           session.refresh() → trae id y created_at de PostgreSQL
        │           camera_mapper.to_entity() → Camera con id=1
        │   (sale del bloque sin error → COMMIT)
        │
        └─ CameraResponseBuilder.build(saved)         builders/response/camera_response_builder.py
              Camera → CameraResponseDTO               dto/response/camera_response_dto.py
  ▼
camera_router.py → CameraResponse.model_validate(dto)   schemas/camera_response.py
  ▼
FastAPI serializa → 201 { "id": 1, "name": "Entrada", "code": "CAM-001", ... }
  ▼
get_session() cierra la sesión
```

### Si el código ya existe

```
use_cases/camera/create_camera.py lanza CameraCodeAlreadyExistsError("CAM-001")
  → sqlalchemy_transaction_manager.py hace ROLLBACK
  → camera_router.py no la captura
  → exception_handlers.py → camera_error_handler() → 409
  → { "detail": "Ya existe una cámara con el código 'CAM-001'" }
```

### Diferencias en los demás endpoints

| Endpoint | Caso de uso | Diferencia con el flujo de creación |
|---|---|---|
| `GET /cameras` | `ListCamerasUseCase` | Sin transacción; `repository.search()` hace un `COUNT` + la página con `OFFSET`/`LIMIT` |
| `GET /cameras/{id}` | `ShowCameraByIdUseCase` | Sin transacción ni body; 404 si no existe |
| `PUT /cameras/{id}` | `UpdateCameraUseCase` | Carga la cámara → `camera.update()` → valida que el código no lo use **otra** cámara → `save()` hace `UPDATE` |
| `PUT /cameras/{id}/status` | `ChangeCameraStatusUseCase` | Carga la cámara → `camera.change_status()` → `save()` |
| `DELETE /cameras/{id}` | `DeleteCameraUseCase` | Verifica que exista → `repository.delete()` → 204 sin body |

---

## 5. Decisiones y pendientes

- **Borrado físico:** `DELETE` elimina la fila. Para dar de baja sin borrar se usa `PUT /cameras/{id}/status` con `inactive`.
- **Carrera en `code`:** si dos requests crean el mismo código a la vez, el índice único de PostgreSQL lo impide, pero hoy la respuesta es 500 y no 409 (falta mapear el `IntegrityError` que envuelve `asyncpg.UniqueViolationError`).
- **Credenciales en `source_url`:** las URLs RTSP suelen llevar `usuario:contraseña`. Conviene guardarlas aparte (cifradas o en un gestor de secretos) y no devolver la URL completa.
- **Sin auditoría ni tenant:** la tabla no tiene `created_by`/`updated_by` ni `tenant_id`.
- **`location_id` sin FK:** falta añadirla cuando exista la tabla `locations`.

---

## 6. Ejecutar

```
# App (desde C:\Tools\aiva\aiva_api)
uvicorn aiva.main:app --app-dir src --reload
# → http://127.0.0.1:8000/docs

# Tests del módulo
$env:PYTHONPATH="src"; python -m pytest src/aiva/modules/camera/tests
```
