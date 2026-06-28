# Software architecture reference
> A practical guide to full-stack software design: React + FastAPI + Python package + Docker + Azure

---

## Table of contents
1. [Architecture overview](#architecture-overview)
2. [The layers explained](#the-layers-explained)
3. [Repo structure](#repo-structure)
4. [Hooks vs routes](#hooks-vs-routes)
5. [Complete code: one feature end to end](#complete-code-one-feature-end-to-end)
6. [How the backend boots](#how-the-backend-boots)
7. [Scalability principles](#scalability-principles)

---

## Architecture overview

A well-designed full-stack app has six distinct layers. Each has one job and one reason to change.

```
Browser (React)          Server (FastAPI / Python)             Infrastructure
─────────────────        ──────────────────────────────────    ──────────────
Component                API layer  (api/)                     Docker
  └─ Hook                  └─ Middleware                       Azure App Service
       └─ api.ts                └─ Service (services/)         PostgreSQL
                                      └─ Package               Redis
                                           └─ DB (models/)
```

**Request flow:**

```
React hook → POST /api/engineering/calculate → FastAPI route
  → middleware (auth, logging) → service → my_engineering_package
  → write to DB → return row → serialize to JSON → hook sets state
  → component re-renders
```

---

## The layers explained

### Frontend (React)

- Runs entirely in the browser — no direct database access
- Communicates with the backend exclusively over HTTP (JSON)
- Can be served from a CDN anywhere in the world
- Completely replaceable (mobile app, CLI) without touching the backend

**Key folders:**
- `components/` — pure UI pieces, no API calls, no business logic
- `pages/` — assembles components, calls hooks, knows about routing
- `hooks/` — the **only** place that makes HTTP requests
- `api.ts` — one file with the base URL and fetch wrapper

### API layer (FastAPI `api/`)

- The HTTP surface your clients call
- Validates incoming requests (Pydantic does this automatically)
- Calls services — contains **no business logic itself**
- Returns structured JSON responses
- A route body should be ~3 lines: validate → delegate → return

### Middleware

Runs on **every request** before your route handler, in pipeline order:

| Middleware | Job |
|---|---|
| CORS | Allow browser requests from your frontend domain |
| Auth | Verify JWT token — rejects unauthenticated requests early |
| Logging | Record every request/response with trace ID |
| Rate limiter | Block abusive clients before they reach your logic |

> **Execution order:** middleware is added outermost-first. CORS must be added first so it handles browser preflight `OPTIONS` requests before auth can reject them.

### Business logic (`services/`)

- Where your application's actual purpose lives
- Plain Python functions/classes — no HTTP, no SQL directly
- Receives plain Python objects, returns plain Python objects
- Calls `my_engineering_package` for domain calculations
- **Testable without starting a server or connecting to a database**

### Data layer

- **PostgreSQL** — the only place data outlives a request. Source of truth.
- **Redis** — cache for frequently-read data. First request hits DB and stores in Redis; subsequent requests return the cached copy in microseconds.
- All other layers are stateless — kill and restart any of them and nothing is lost.

### Docker + Azure

- Docker packages your app with everything it needs to run (OS libs, Python version, dependencies)
- Same image runs identically on your laptop, CI, and Azure
- Each service gets its own container: React/nginx, FastAPI/uvicorn, PostgreSQL, Redis
- Azure App Service takes your image and provides: load balancing, auto-scaling, TLS, health monitoring
- Azure Landing Zones = pre-hardened environment with networking, firewall, RBAC already configured by your org

---

## Repo structure

```
my-app/
│
├── packages/                          ← shared code, outside the app
│   └── my_engineering_package/
│       ├── __init__.py                ← public API exports
│       ├── core.py                    ← main calculation logic
│       ├── models.py                  ← plain Python dataclasses (no SQLAlchemy)
│       ├── exceptions.py              ← InvalidInputError, CalculationError
│       ├── setup.py                   ← makes it pip-installable
│       └── tests/                     ← package tests, zero app dependencies
│
├── frontend/                          ← standalone React app
│   ├── src/
│   │   ├── api.ts                     ← base URL + fetch wrapper (one file)
│   │   ├── hooks/                     ← ONLY place that calls the backend
│   │   ├── components/                ← pure UI, no API calls
│   │   └── pages/                     ← assembles components + calls hooks
│   └── Dockerfile                     ← builds React → nginx serves static files
│
├── backend/                           ← FastAPI application
│   ├── app/
│   │   ├── main.py                    ← creates app, registers middleware + routers
│   │   ├── config.py                  ← reads env vars (Pydantic BaseSettings)
│   │   ├── db.py                      ← engine, SessionLocal, get_db()
│   │   ├── api/                       ← HTTP routes (one file per domain)
│   │   ├── services/                  ← business logic (calls package + DB)
│   │   ├── models/
│   │   │   ├── orm.py                 ← SQLAlchemy table definitions
│   │   │   └── schemas.py             ← Pydantic request/response shapes
│   │   └── middleware/                ← auth.py, logging.py, rate_limit.py
│   ├── tests/                         ← mirrors app/ structure
│   ├── requirements.txt               ← includes: -e ../../packages/my_engineering_package
│   └── Dockerfile                     ← multi-stage build, non-root user, health check
│
├── docker-compose.yml                 ← runs entire system: docker compose up
├── .env.example                       ← template for all required env vars
├── .gitignore                         ← node_modules/, __pycache__/, .env, *.egg-info/
└── README.md                          ← clone → cp .env.example .env → docker compose up
```

### The one rule that governs structure

> Each folder has exactly one reason to change.

- `api/` changes when your HTTP surface changes
- `services/` changes when your business rules change
- `models/` changes when your database schema changes
- `packages/` changes when your domain logic changes

If changing one thing forces you to touch files in three folders, the boundary is wrong.

### Why `packages/` sits at the repo root

The package doesn't belong to the backend — it's *used* by it. Placing it at the root means:
- A second backend service, a CLI, or a data pipeline can all install from the same place
- `requirements.txt` gets one line: `-e ../../packages/my_engineering_package`
- The Dockerfile copies `packages/` before `app/` so Docker layer caching works (dependencies change rarely, code changes often)

---

## Hooks vs routes

**They are not the same thing — they are mirror images of the same HTTP call.**

```
Browser                              │  Server
─────────────────────────────────────│─────────────────────────────────────
Component                            │
  calls hook                         │
    hook calls api.ts ───────────────┼──► FastAPI route receives request
      POST /api/engineering/calculate│      validates body (Pydantic)
                                     │      calls service
    hook receives JSON ◄─────────────┼──── returns CalculationResponse
  hook sets React state              │
Component re-renders                 │
                                     │
         ◄─── network boundary ─────►│
```

| | Hook (TypeScript) | Route (Python) |
|---|---|---|
| Lives in | Browser | Server |
| Job | Fire the HTTP request, own loading/error/result state | Receive the HTTP request, validate, delegate, respond |
| Knows about | The URL and shape of the JSON | The URL and shape of the JSON |
| Does NOT know | What the server does with the data | That React exists |
| Analogy | The caller | The receiver |

> A hook is the TypeScript version of `requests.post()`. A route is not the Python version of a hook — there is no frontend equivalent to a route because the frontend never *receives* incoming requests.

---

## Complete code: one feature end to end

### `packages/my_engineering_package/core.py`

```python
from dataclasses import dataclass

@dataclass
class CalculationInput:
    material: str
    load_kn: float
    length_m: float

@dataclass
class CalculationResult:
    stress_mpa: float
    is_safe: bool
    safety_factor: float

def calculate_stress(inp: CalculationInput) -> CalculationResult:
    area = 0.01  # m² — simplified
    stress = (inp.load_kn * 1000) / area
    safety_factor = 250 / stress  # yield strength / stress
    return CalculationResult(
        stress_mpa=round(stress / 1e6, 4),
        is_safe=safety_factor >= 1.5,
        safety_factor=round(safety_factor, 3),
    )
```

**Why:** pure function, no framework dependencies, same input always gives same output. Unit testable with zero mocking.

---

### `backend/app/config.py`

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    redis_url: str = "redis://localhost:6379"
    debug: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
```

**Why:** fields without defaults are required — app crashes at startup with a clear error if they're missing. One import everywhere: `from app.config import settings`. Never `os.environ.get()` scattered through the codebase.

---

### `backend/app/db.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.orm import Base

# One engine per process — manages the connection pool
engine = create_engine(
    settings.database_url,
    pool_size=10,        # keep 10 connections ready
    max_overflow=20,     # allow 20 more in a burst
    pool_pre_ping=True,  # test connections before use, reconnects if stale
)

# Factory — calling it creates a new session
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,  # explicit commits only
    autoflush=False,
)

def init_db():
    """Create all tables that don't exist yet. Called once at startup."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """FastAPI dependency — injects a fresh session into any route that needs one."""
    db = SessionLocal()
    try:
        yield db       # route runs here
    finally:
        db.close()     # always runs — returns connection to pool
```

**Why `yield` not `return`:** FastAPI runs everything before `yield` before the route, passes `db` in, then runs everything after `yield` (the `finally` block) when the route finishes — even if it raised an exception. Without `finally: db.close()`, connections leak until Postgres refuses new ones.

---

### `backend/app/models/orm.py`

```python
from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class Calculation(Base):
    __tablename__ = "calculations"

    id            = Column(Integer, primary_key=True)
    material      = Column(String,  nullable=False)
    load_kn       = Column(Float,   nullable=False)
    stress_mpa    = Column(Float)
    is_safe       = Column(Boolean)
    safety_factor = Column(Float)
```

---

### `backend/app/models/schemas.py`

```python
from pydantic import BaseModel, Field

class CalculationRequest(BaseModel):
    material: str
    load_kn:  float = Field(gt=0, description="Load in kilonewtons")
    length_m: float = Field(gt=0)

class CalculationResponse(BaseModel):
    id:            int
    stress_mpa:    float
    is_safe:       bool
    safety_factor: float

    model_config = {"from_attributes": True}  # read from SQLAlchemy ORM objects
```

**Why two separate model files:** the ORM model is the database row shape. The schema is the HTTP contract. They evolve independently — the DB might store more fields than you expose in the API, and the API might accept fields in a different format than you store them.

---

### `backend/app/services/engineering_service.py`

```python
from sqlalchemy.orm import Session
from my_engineering_package.core import CalculationInput, calculate_stress
from app.models.orm import Calculation

def run_calculation(
    material: str,
    load_kn: float,
    length_m: float,
    db: Session,
) -> Calculation:

    # 1. call the package — pure calculation
    inp = CalculationInput(material=material, load_kn=load_kn, length_m=length_m)
    result = calculate_stress(inp)

    # 2. persist to DB
    row = Calculation(
        material=material,
        load_kn=load_kn,
        stress_mpa=result.stress_mpa,
        is_safe=result.is_safe,
        safety_factor=result.safety_factor,
    )
    db.add(row)
    db.commit()
    db.refresh(row)  # loads the auto-generated id

    # 3. return the ORM row — route converts it to JSON
    return row
```

**Why the DB session is passed in, not created here:** dependency injection. In tests, you pass a test DB session. The service never knows if it's talking to a real Postgres or an in-memory SQLite. This is what makes it unit testable.

---

### `backend/app/api/engineering.py`

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.schemas import CalculationRequest, CalculationResponse
from app.services.engineering_service import run_calculation

router = APIRouter(prefix="/api/engineering", tags=["engineering"])

@router.post("/calculate", response_model=CalculationResponse)
def calculate(
    body: CalculationRequest,       # Pydantic validates + parses JSON body
    db: Session = Depends(get_db),  # FastAPI injects + closes DB session
):
    row = run_calculation(
        material=body.material,
        load_kn=body.load_kn,
        length_m=body.length_m,
        db=db,
    )
    return row  # FastAPI + response_model serializes automatically
```

**Why this file is so short:** the route does exactly three things — validate, delegate, respond. If you find yourself writing logic here, it belongs in the service. `response_model=CalculationResponse` filters out any ORM fields not in the schema, so the client only sees what you intend.

---

### `backend/app/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.db import init_db
from app.config import settings
from app.middleware.auth import AuthMiddleware
from app.middleware.logging import LoggingMiddleware
from app.api import engineering

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()           # create tables on boot
    print("DB ready")
    yield               # app runs here
    print("Shutting down")

app = FastAPI(
    title="My Engineering App",
    version="1.0.0",
    lifespan=lifespan,
)

# Middleware — outermost (added first) runs first on requests
# CORS must be outermost so it handles preflight OPTIONS before auth rejects them
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)
app.add_middleware(AuthMiddleware)

# Routers — each domain registers itself, main.py just mounts them
app.include_router(engineering.router)

# Health check — Azure App Service pings this to decide if the container is alive
@app.get("/health")
def health():
    return {"status": "ok"}
```

---

### `frontend/src/api.ts`

```typescript
const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000"

export const api = {
  async post<T>(path: string, body: unknown): Promise<T> {
    const res = await fetch(`${BASE_URL}${path}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("token") ?? ""}`,
      },
      body: JSON.stringify(body),
    })
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
    return res.json()
  },
}
```

**Why one file:** when the backend URL changes, you change one line. When auth headers change, you change one place. Nothing else imports `fetch` directly.

---

### `frontend/src/hooks/useEngineering.ts`

```typescript
import { useState } from "react"
import { api } from "../api"

interface CalcInput {
  material: string
  load_kn: number
  length_m: number
}

interface CalcResult {
  id: number
  stress_mpa: number
  is_safe: boolean
  safety_factor: number
}

export function useEngineering() {
  const [result, setResult]   = useState<CalcResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState<string | null>(null)

  async function calculate(input: CalcInput) {
    setLoading(true)
    setError(null)
    try {
      const data = await api.post<CalcResult>("/api/engineering/calculate", input)
      setResult(data)
    } catch (e: any) {
      setError(e.message ?? "Something went wrong")
    } finally {
      setLoading(false)  // always runs — spinner never gets stuck
    }
  }

  return { result, loading, error, calculate }
}
```

**Why `finally` for `setLoading(false)`:** without it, if the request throws, loading stays `true` forever and the user sees a stuck spinner. `finally` always runs regardless of success or failure.

---

### `frontend/src/pages/EngineeringPage.tsx`

```tsx
import { useState } from "react"
import { useEngineering } from "../hooks/useEngineering"

export function EngineeringPage() {
  const { result, loading, error, calculate } = useEngineering()

  // Local form state — UI state, separate from server state
  const [material, setMaterial] = useState("steel")
  const [load, setLoad]         = useState(50)
  const [length, setLength]     = useState(2)

  function handleSubmit() {
    calculate({ material, load_kn: load, length_m: length })
  }

  return (
    <div>
      <input value={material} onChange={e => setMaterial(e.target.value)} />
      <input
        type="number"
        value={load}
        onChange={e => setLoad(Number(e.target.value))}
      />
      <button onClick={handleSubmit} disabled={loading}>
        {loading ? "Calculating..." : "Calculate"}
      </button>

      {/* Always handle all three states explicitly */}
      {error  && <p style={{ color: "red" }}>{error}</p>}
      {result && (
        <div>
          <p>Stress: {result.stress_mpa} MPa</p>
          <p>Safe: {result.is_safe ? "Yes" : "No"}</p>
          <p>Safety factor: {result.safety_factor}</p>
        </div>
      )}
    </div>
  )
}
```

**Why the component is so clean:** it imports the hook, gets `{ result, loading, error, calculate }`, and renders. No fetch, no URLs, no JSON parsing. If the API changes, only the hook changes — not this file.

---

## How the backend boots

When `uvicorn app.main:app` runs, this is the exact sequence:

| Step | What happens | Why it matters |
|---|---|---|
| 1 | `config.py` loads | Reads env vars. Crashes immediately if required vars are missing — fail fast, not mysteriously later |
| 2 | `db.py` loads | Creates SQLAlchemy engine + connection pool using the URL from settings |
| 3 | `main.py` loads | Imports all routers and middleware — wires the app together in memory |
| 4 | `lifespan` runs | `init_db()` fires — creates any missing DB tables |
| 5 | uvicorn starts listening | Port 8000 opens. Azure health check hits `/health`. If 200, traffic starts routing in |
| 6 | Request arrives | CORS → logging → auth middleware run. Then `get_db()` opens a session. Route runs. Session closes |
| 7 | Shutdown signal | `lifespan` resumes after `yield` — cleanup runs, connection pool drains gracefully |

---

## Scalability principles

These are not premature optimisations — they are the architectural decisions that determine whether you can scale horizontally at all.

### Stateless services

Every layer except the database holds no state between requests. Each request arrives with everything needed to process it (e.g. a JWT token). This means you can run 10 identical FastAPI containers — any of them can handle any request. If your service holds state in memory (e.g. a user session dict), you're locked to one instance.

### Connection pooling

`db.py` keeps a pool of open Postgres connections (`pool_size=10`). Opening a new TCP connection to Postgres takes ~5–20ms. At 100 requests/second that adds up. The pool reuses connections — a request grabs one, uses it, returns it. Without a pool you'd open and close a connection on every request.

### Caching (Redis)

The first request for a piece of data hits the DB and stores the result in Redis. Every subsequent request gets the cached copy in microseconds. The most impactful architectural lever for read-heavy apps. Add it early — retrofitting cache invalidation into an existing service is painful.

### What scales automatically with this architecture

Because every layer is stateless and containerised:
- Adding more FastAPI instances is one config change in Azure (horizontal scaling)
- The frontend is static files served by nginx — CDN-cacheable globally
- Middleware runs per-request with no shared state — scales with the instances

### What becomes the bottleneck first

1. **Database write throughput** — single primary, not horizontally scalable. Mitigation: read replicas, connection pooling (already in place), async DB drivers (`asyncpg`)
2. **Cache miss rate** — if Redis isn't caching effectively, every request hits the DB. Monitor hit rate
3. **API instance memory** — if a service loads large objects into memory per-request, instances fill up fast

---

## Key principles to remember

> **Each file has one reason to change.** If changing business logic touches the route file, the structure is wrong. If changing the DB schema touches the service, the structure is wrong.

> **The package is not part of the app.** It's a tool the app uses. It has no knowledge of FastAPI, HTTP, or databases.

> **Routes are thin.** Validate → delegate → return. Three lines. If a route is long, something belongs in services/.

> **Hooks own server state on the frontend.** Components never call fetch(). They call hooks. Hooks call api.ts. api.ts calls fetch(). One direction, one level at a time.

> **Stateless everything except the DB.** The database is the only place data should live between requests. Everything else should be restartable at any time with no data loss.