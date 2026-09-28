# Arquitectura y flujo de una petición

Guía general, aplicable a **cualquier módulo** de `aiva_api`. Describe las capas, cómo viaja una petición entre archivos y qué reglas seguir al crear un módulo nuevo.

En los ejemplos, `{module}` es el nombre del módulo (ej. `camera`) y `{entity}` la entidad (ej. `camera`, `Camera`).

---

## 1. Visión general

La API sigue **DDD + arquitectura hexagonal**, organizada por módulos:

```
src/aiva/
├── main.py                  # crea la app y registra cada módulo
├── config/                  # configuración (settings leídos de .env)
├── database/                # infraestructura técnica de BD, común a todos los módulos
├── testing/                 # dobles de prueba genéricos
└── modules/
    └── {module}/
        ├── module.py        # registro del módulo (≈ ServiceProvider de Laravel)
        ├── domain/          # reglas de negocio puras
        ├── application/     # casos de uso y orquestación
        ├── infrastructure/  # adaptadores: HTTP, BD, servicios externos
        └── tests/
```

### Paquetes técnicos fuera de los módulos

No existe un paquete `shared/`: eso evita un *God module*. Cada pieza técnica va en un paquete cuyo nombre dice qué puede contener:

| Paquete | Contenido permitido |
|---|---|
| `aiva/config/` | Settings de la aplicación |
| `aiva/database/` | `Base` declarativa común, `engine`/`SessionFactory`/`get_session`, `SqlAlchemyTransactionManager` |
| `aiva/testing/` | Dobles de prueba genéricos (ej. `TransactionManagerStub`) |

Reglas:
- Estos paquetes **no importan nada de `modules/`** y no contienen lógica de negocio.
- Si aparece una nueva necesidad técnica, se crea un paquete nuevo con nombre propio (ej. `aiva/cache/`), en lugar de crecer uno genérico.

---

## 2. Capas de un módulo

```
modules/{module}/
├── module.py
├── domain/
│   ├── entities/            # entidades con métodos de negocio
│   ├── value_objects/       # tipos inmutables que se autovalidan
│   ├── enums/               # estados y tipos (sin números mágicos)
│   ├── exceptions/          # excepciones tipadas; una base {Module}Error
│   ├── repositories/        # puertos de persistencia (Protocol)
│   ├── policies/            # reglas de negocio complejas (opcional)
│   ├── ports/               # puertos a servicios externos (opcional)
│   └── events/              # eventos de dominio (opcional)
├── application/
│   ├── contracts/           # puertos que necesita la aplicación (ej. TransactionManager)
│   ├── dto/                 # datos de entrada, @dataclass(frozen=True, slots=True)
│   │   └── response/        # datos de salida
│   ├── builders/            # dict → DTO
│   │   └── response/        # entidad → DTO de respuesta
│   └── use_cases/{entity}/  # una clase por acción
├── infrastructure/
│   ├── http/
│   │   ├── routers/         # endpoints FastAPI (delgados)
│   │   ├── schemas/         # validación Pydantic de entrada/salida
│   │   │   └── concerns/    # campos reutilizables entre schemas
│   │   ├── dependencies.py  # wiring: sesión → repositorio → caso de uso
│   │   └── exception_handlers.py  # excepción de dominio → código HTTP
│   └── persistence/sqlalchemy/
│       ├── models/          # modelos SQLAlchemy (heredan de aiva.database.base.Base)
│       ├── mappers/         # modelo ↔ entidad
│       └── repositories/    # implementación de los puertos de domain/repositories
└── tests/
    ├── conftest.py
    ├── fakes.py             # repositorios en memoria del módulo
    └── unit/
        ├── domain/
        └── use_cases/
```

### Qué puede importar cada capa

| Capa | Puede importar | No puede importar |
|---|---|---|
| `domain` | Solo Python estándar y su propio `domain` | FastAPI, SQLAlchemy, Pydantic, `application`, `infrastructure`, otros módulos |
| `application` | Su `domain` (y el `domain` de otros módulos si es imprescindible) | FastAPI, SQLAlchemy, Pydantic, `infrastructure` |
| `infrastructure` | Todo: su `domain`, su `application`, `aiva.database`, `aiva.config`, frameworks | — |

```
infrastructure  ──importa──►  application  ──importa──►  domain
                                                            ▲
infrastructure ─────────── implementa los puertos ──────────┘
```

---

## 3. Responsabilidad de cada pieza

| Pieza | Responsabilidad | No debe |
|---|---|---|
| **Schema** (Pydantic) | Validar forma del JSON: tipos, longitudes, enums, campos extra | Contener reglas de negocio |
| **Router** | Recibir el request, llamar builder → caso de uso, devolver el schema de respuesta | Tener lógica, try/except o acceso a BD |
| **Builder** | Convertir un `dict` en un DTO y normalizar valores vacíos o por defecto | Validar reglas de negocio |
| **DTO** | Transportar datos inmutables entre capas | Tener comportamiento |
| **Caso de uso** | Orquestar: cargar entidad → llamar método de negocio → guardar, dentro de una transacción | Conocer HTTP o SQL |
| **Entidad / Value object** | Reglas de negocio e invariantes | Conocer la BD o el framework |
| **Puerto** (`Protocol`) | Declarar qué necesita el dominio o la aplicación | Tener implementación |
| **Repositorio SQLAlchemy** | Implementar el puerto; traducir con el mapper | Tener try/except o lógica de negocio |
| **Mapper** | Traducir modelo ↔ entidad | — |
| **Exception handler** | Traducir `{Module}Error` → código HTTP | — |
| **`module.py`** | Registrar routers y exception handlers en la app | — |

---

## 4. Flujo de una petición de escritura

```
Cliente
  │  POST/PUT /api/v1/{recurso}   { ...json... }
  ▼
main.py ── la app ya tiene el router registrado por {module}/module.py
  ▼
routers/{entity}_router.py → endpoint(body, use_case)
  │
  ├─① FastAPI valida el body con schemas/{accion}_{entity}_request.py
  │     ✗ tipo/longitud/enum inválido → 422 automático (no llega al caso de uso)
  │
  ├─② FastAPI resuelve Depends(get_{accion}_{entity}_use_case)   http/dependencies.py
  │       get_session()                 aiva/database/session.py   (una AsyncSession por request)
  │         ├─ get_{entity}_repository()  → SqlAlchemy{Entity}Repository(session)
  │         └─ get_transaction_manager()  → SqlAlchemyTransactionManager(session)
  │       → {Accion}{Entity}UseCase(repository, transaction_manager)
  │     (FastAPI cachea dependencias por request: todos comparten la MISMA sesión)
  │
  ├─③ {Accion}{Entity}Builder.build(body.model_dump())     application/builders/
  │       dict → {Accion}{Entity}DTO                        application/dto/
  │
  └─④ use_case.execute(dto)                                 application/use_cases/{entity}/
        │
        ├─ Construye value objects y entidad                domain/value_objects/, domain/entities/
        │     ✗ regla rota → Invalid{Entity}Error
        │
        ├─ async with transaction_manager.transaction():    aiva/database/sqlalchemy_transaction_manager.py
        │     ├─ repository.find_by_…()                     infrastructure/persistence/sqlalchemy/repositories/
        │     │     SELECT → mapper.to_entity()
        │     ├─ entidad.metodo_de_negocio()                domain/entities/
        │     └─ repository.save(entidad)
        │           mapper.apply_to_model() → flush (INSERT/UPDATE) → refresh → mapper.to_entity()
        │   sin error → COMMIT   |   excepción → ROLLBACK
        │
        └─ {Entity}ResponseBuilder.build(entidad)          application/builders/response/
              entidad → {Entity}ResponseDTO                application/dto/response/
  ▼
router → {Entity}Response.model_validate(dto)              schemas/{entity}_response.py
  ▼
FastAPI serializa → 200/201 JSON
  ▼
get_session() cierra la sesión
```

### Petición de lectura

Sigue el mismo camino, pero sin transacción: el caso de uso recibe solo el repositorio.

```
router → [schema] → builder → UseCase(repository).execute(dto | id)
           → repository.find_by_id / search → mapper.to_entity()
           → ResponseBuilder → DTO → schema de respuesta → JSON
```

---

## 5. Flujo de errores

No hay `try/except` en routers, casos de uso ni repositorios. Las excepciones suben solas:

```
Excepción de dominio ({Module}Error o subclase) lanzada en entidad / VO / caso de uso
  → si estaba dentro de transaction() → ROLLBACK
  → atraviesa el router sin capturarse
  → infrastructure/http/exception_handlers.py  (registrado por module.py)
       {Entity}NotFoundError          → 404
       {Entity}…AlreadyExistsError    → 409
       Invalid{Entity}Error           → 422
       otra subclase de {Module}Error → 400
  → { "detail": "<mensaje de la excepción>" }
```

| Origen del error | Quién lo detecta | Respuesta |
|---|---|---|
| JSON mal formado, tipos o enums inválidos | Schema Pydantic (FastAPI) | 422 con el detalle de los campos |
| Regla de negocio rota | Entidad / value object | 422 (`Invalid{Entity}Error`) |
| Recurso inexistente | Caso de uso | 404 |
| Conflicto (ej. código único) | Caso de uso | 409 |
| Error no previsto | — | 500 |

---

## 6. Tests: por qué funciona sin base de datos

El caso de uso depende de **puertos** (`Protocol`), no de implementaciones. En producción, `dependencies.py` le inyecta las reales. En tests se le pasan dobles:

| Puerto | Producción | Test |
|---|---|---|
| `{Entity}Repository` | `SqlAlchemy{Entity}Repository` | `InMemory{Entity}Repository` (`{module}/tests/fakes.py`) |
| `TransactionManager` | `SqlAlchemyTransactionManager` (`aiva/database/`) | `TransactionManagerStub` (`aiva/testing/`) |

Como `Protocol` es **tipado estructural**, una sola implementación de `aiva/database/` o `aiva/testing/` cumple el puerto de cualquier módulo sin que el módulo importe nada de fuera de su `application/contracts/`.

Los repositorios en memoria deben devolver **copias** de las entidades (`dataclasses.replace`). Así, mutar una entidad leída no altera lo "persistido", igual que con la BD real.

```
$env:PYTHONPATH="src"; python -m pytest src/aiva/modules/{module}/tests
```

---

## 7. Checklist para crear un módulo nuevo

1. **Migración:** `database/flyway/{module}/V{yyMMddHHmmss}__create_{tabla}.sql`, y añadir `filesystem:./{module}` a `flyway.locations`.
2. **Domain:** enums, excepción base `{Module}Error` y sus subclases, value objects, entidad y el puerto `{Entity}Repository` (`Protocol`).
3. **Application:**
   - `contracts/transaction_manager.py`: el puerto (copia del `Protocol`, sin implementación).
   - DTOs de entrada y salida.
   - Builders.
   - Un caso de uso por acción en `use_cases/{entity}/`.
4. **Infrastructure / persistencia:** modelo (hereda de `aiva.database.base.Base`), mapper y repositorio SQLAlchemy.
5. **Infrastructure / HTTP:** schemas (campos comunes en `concerns/`), `dependencies.py`, router y `exception_handlers.py`.
6. **`module.py`:** `register(app)` incluye los routers con `prefix="/api/v1"` y registra los exception handlers.
7. **`main.py`:** `from aiva.modules.{module} import module as {module}_module` y `{module}_module.register(app)`.
8. **Tests:** `tests/fakes.py` con el repositorio en memoria, y tests de domain y de casos de uso.

---

## 8. Convenciones

- **Rutas:**
  - `POST /{recurso}` crea.
  - `POST /{recurso}/list` lista (filtros en el body).
  - `GET /{recurso}/{id}` consulta uno.
  - `PUT /{recurso}/{id}` actualiza.
  - `PUT /{recurso}/{id}/status` cambia el estado.
  - `DELETE /{recurso}/{id}` borra (responde 204).
- **Path params numéricos** con convertidor: `"/{id:int}"`, para que no choquen con rutas fijas como `/health`.
- **Listados:** responden `{ "data": [...], "count": N }`, con paginación `offset` / `limit`.
- **Errores:** `{ "detail": "..." }`, el mismo formato que usa FastAPI por defecto.
- **Nombres:**
  - Casos de uso: `{Accion}{Entity}UseCase` en `{accion}_{entity}.py`.
  - Repositorio real: `SqlAlchemy{Entity}Repository`.
  - Excepciones: terminan en `Error`.
- **Ejecutar:** `uvicorn aiva.main:app --app-dir src --reload`.
