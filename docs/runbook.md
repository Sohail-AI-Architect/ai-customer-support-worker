# Runbook

> Local development and operations for the AI Customer Support Worker. See
> `specs/001-ai-support-worker/quickstart.md` for the first-run quickstart.
> Migrations live at the repo root under `migrations/` (Alembic).

## Prerequisites

- Docker Desktop (Windows) with Postgres container running
- `uv` (Python env/package manager), `node` + `npm` (frontend)
- A `.env` file from `.env.example` (never commit `.env`)

## Start the stack

```bash
docker compose up        # starts postgres, backend, frontend (+ mcp servers)
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- OpenAPI docs: http://localhost:8000/docs

Or run the backend directly (dev):

```bash
cd backend && PYTHONPATH=src uv run uvicorn main:app --port 8000
```

## Database migrations

Migrations are managed with **Alembic** at the repo root.

```bash
# From the repo root
uv run --project backend alembic upgrade head   # apply all migrations
uv run --project backend alembic current        # show current revision
uv run --project backend alembic history        # list revisions
```

The initial migration creates all tables: customers, users, support_tickets,
conversations, conversation_messages, knowledge_articles, escalations,
approval_requests, worker_action_log.

To verify the migrations are in sync with the ORM models:

```bash
uv run --project backend alembic check
# -> "No new upgrade operations detected."
```

## Seed data

```bash
# Knowledge articles (starter FAQ set) — required for answering
cd backend && PYTHONPATH=src uv run python -m services.seed_knowledge

# Demo human agent (for the agent queue UI) — idempotent
cd backend && PYTHONPATH=src uv run python -m services.seed_demo
```

## Run the tests

```bash
cd backend && PYTHONPATH=src uv run pytest -q          # backend suite
# mcp-servers (run from each server dir so its pyproject pythonpath applies):
for s in knowledge-server support-data-server escalation-approval-server; do
  (cd "mcp-servers/$s" && uv run --project ../../backend python -m pytest tests -q)
done
```

Lint:

```bash
cd backend && uv run ruff check src tests
```

## End-to-end UI smoke (Playwright)

Requires the frontend (3000) and backend (8000) running. From `frontend/`:

```bash
npm install
npx playwright install chromium
npm run e2e     # customer answer / escalation resolve / approval approve
```

## Containers

Dockerfiles ship per component (T059): `backend/Dockerfile`, `frontend/Dockerfile`,
`mcp-servers/Dockerfile` (build from repo root). Compose runs backend with
`uv run uvicorn main:app` (the uv venv is not on PATH, so the `uv run` prefix is
required). The MCP servers are consumed via in-process adapters today; the
stdio/HTTP transport bridge is the remaining wiring (see
`backend/src/mcp/__init__.py`). Migrations/schema are applied with Alembic (above)
— `docker compose up` expects a migrated DB.

## Run the evaluation

The golden eval grades the Worker against `eval/golden_set.json`. It requires a
live backend for ticket/escalation cases.

```bash
# From repo root, backend running on :8000
uv run --project backend python eval/run_eval.py
# Worker-only (no HTTP server) for knowledge/chat cases:
PYTHONPATH=backend/src:. uv run --project backend python eval/run_eval.py --no-api
```

Reports pass rate and **containment** (escalation rate) — a core success metric.

## Common operations

| Task | Command |
|------|---------|
| Reset the DB to migrations | drop schema, `alembic upgrade head`, reseed |
| Generate a new migration | `uv run --project backend alembic revision --autogenerate -m "<desc>"` |
| Chat smoke test | `POST /api/chat` (see `docs/api.md`) |
| Agent queue | open `http://localhost:3000/agent` |

## Troubleshooting

- **Tests lose seeded knowledge**: the pytest `db_engine` fixture drops/recreates
  tables per session — reseed knowledge after running tests that touch it.
- **No answers in eval after test runs**: same cause; run `services.seed_knowledge`
  again.
- **Port in use**: `taskkill //F //IM python.exe` (Windows) then restart uvicorn.
- **Postgres down**: `docker compose up -d postgres`.

## See also

- Architecture: `docs/architecture.md`
- API usage: `docs/api.md`
- Security hardening review: `docs/security-review.md`
- ADRs: `history/adr/`
