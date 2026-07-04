# AI Blog Platform

A multi-user platform where authors generate **5-minute-read** blog posts with an
AI agent (Pydantic AI + Azure AI Foundry), review/edit the result, and publish.

Built as a clean, layered full-stack app: **React + FastAPI + a framework-free
Python package**, containerised for Azure.

---

## Architecture

```
frontend/ (React)          backend/ (FastAPI)                packages/
─────────────────          ──────────────────────────────    ──────────────────
component                  api/      thin HTTP routes        blog_ai_agent/
  └─ hook                    └─ services/  business logic       (Pydantic AI +
       └─ src/client/          └─ repositories (db.py)          Azure Foundry)
          (generated)             └─ models/orm.py
```

The single rule: **each layer has one reason to change.**

| Layer | Folder | Job |
|---|---|---|
| AI domain | `packages/blog_ai_agent/` | Turn a `BlogBrief` into a validated `BlogDraft`. Knows nothing about HTTP/DB. |
| HTTP routes | `backend/app/api/` | Validate → delegate → return. ~3 lines each. |
| Business logic | `backend/app/services/` | Draft lifecycle, auth, publishing. No HTTP, no raw SQL. |
| Data | `backend/app/models/orm.py` + `db.py` | SQLAlchemy 2.0 async + Postgres. |
| Contracts | `backend/app/models/schemas.py` | Pydantic request/response shapes. |
| UI | `frontend/src/` | Components → hooks → generated client (`src/client/`). Only hooks touch the network. |

### The authoring flow

```
register/login → create draft (brief) → POST /generate (AI agent runs)
  → review & edit generated Markdown → publish → public post
```

A draft moves through states: `pending → generating → ready → published`
(or `failed`). The state machine lives in `services/draft_service.py`.

---

## Quick start (Docker)

```bash
cp .env.example .env
# Fill in AZURE_OPENAI_* values, then:
docker compose up --build
```

- Frontend: http://localhost:8080
- API + docs: http://localhost:8000/docs

## Local development (without Docker)

**Backend**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ../packages/blog_ai_agent
pip install -e ".[dev]"
export $(grep -v '^#' ../.env | xargs)   # or set vars manually
uvicorn app.main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

## Frontend API client (generated)

The frontend never hand-writes fetch calls or API types. `frontend/src/client/`
is fully generated from the backend's OpenAPI schema via
[hey-api](https://heyapi.dev) (`@hey-api/openapi-ts`) and includes:

- Typed request functions per endpoint (`sdk.gen.ts`) and response/schema types
  (`types.gen.ts`) — one-to-one with the backend's Pydantic schemas.
- Ready-made [TanStack Query](https://tanstack.com/query) options
  (`src/client/@tanstack/react-query.gen.ts`): a `*Options()` factory for every
  `GET` route (e.g. `listPostsOptions()`, `getDraftOptions()`) to drop straight
  into `useQuery`, and a `*Mutation()` factory for every write route (e.g.
  `createDraftMutation()`, `publishDraftMutation()`) to drop into `useMutation`.
  Matching `*QueryKey()` functions (e.g. `listDraftsQueryKey()`) are used for
  cache updates/invalidation — for example, publishing a draft invalidates both
  the drafts list and the posts list so `HomePage` picks up the new post.
- Pages consume these directly, e.g.:
  ```ts
  const { isPending, error, data: posts = [] } = useQuery(listPostsOptions())
  ```

Only two files under `src/client/` are hand-written (not regenerated):
`setup.ts` (configures the client's base URL and attaches the auth token to
every request) and `errors.ts` (turns the error body the client throws into a
displayable message). Everything else is generated output and should not be
edited directly.

**Whenever you change a backend route or Pydantic schema**, regenerate the
client so the frontend stays in sync:

```bash
# 1. Export the backend's OpenAPI schema to frontend/openapi.json
uv run --package blog-platform-backend python backend/scripts/export_openapi.py

# 2. Regenerate the typed client from that schema
cd frontend && npm run generate-client
```

No running Postgres/Azure connection is required for step 1 — the export
script only imports the FastAPI app to read its route definitions.

## Tests

```bash
# AI package — pure unit tests, no network
cd packages/blog_ai_agent && pytest

# Backend — full API flow against in-memory SQLite + a fake AI writer
cd backend && pytest
```

The backend tests prove the design goal: the whole register → generate →
publish flow runs **without Postgres and without Azure**, because the DB session
and the AI writer are injected dependencies (`app/dependencies.py`, `app/ai.py`).

---

## Key design decisions

- **The AI agent is a standalone package.** `blog_ai_agent` has no FastAPI/DB
  imports, so it is unit-testable and reusable (CLI, batch jobs, a second service).
- **Structured AI output.** The agent must return a Pydantic `BlogDraft`; invalid
  output fails loudly rather than persisting garbage.
- **Async end to end.** AI calls are I/O-bound, so the stack is async
  (FastAPI + async SQLAlchemy + asyncpg) to avoid blocking the event loop.
- **Auth via JWT.** Stateless tokens → the API scales horizontally with no shared
  session store.
- **Generated, typed API client.** The frontend's `src/client/` is generated
  from the backend's OpenAPI schema (hey-api), pairing typed request functions
  with TanStack Query options/mutations, so request/response types and query
  cache keys can't drift out of sync with the actual API contract.
- **Domain errors, not HTTP, in services.** `app/errors.py` defines `AppError`
  subclasses mapped to status codes in `main.py`, keeping services HTTP-free.

## Production notes

- Swap `init_db()`'s `create_all` for **Alembic** migrations.
- Put **Redis** in front of the public post reads (`GET /api/posts`).
- Move AI generation to a **background worker/queue** if generation latency hurts
  UX; the `generation` state already models this (poll `GET /api/drafts/{id}`).
