# Quickstart — AI Customer Support Worker

First-run, end-to-end setup: Postgres → migrate → seed → run → test → evaluate.
Covers US1–US5 (answer, retrieve, create ticket, escalate, approve).

> **Scope note**: T063 validates this quickstart against a live Postgres and
> Docker stack. All commands assume Docker Desktop / Postgres is up.
> Finalized in Phase 8; replaces the earlier "Phase 1 output" draft.

## 0. Prerequisites

- Docker Desktop (Windows) running
- `uv` (Python), `node` + `npm` (frontend)
- Git

## 1. Clone and configure

```bash
git checkout 001-ai-support-worker
cp .env.example .env        # git-ignored; edit SESSION_SECRET when away from localhost
```

## 2. Postgres

```bash
docker compose up -d postgres      # wait until healthy: docker compose ps
```

## 3. Migrate (schema)

```bash
uv run --project backend alembic upgrade head   # create all tables
uv run --project backend alembic check          # expect "No new upgrade operations detected."
```

## 4. Seed

```bash
# Approved knowledge (required to answer common questions) + demo human agent
cd backend && PYTHONPATH=src uv run python -m services.seed_knowledge
cd backend && PYTHONPATH=src uv run python -m services.seed_demo
```

## 5. Run the stack

```bash
docker compose up -d        # backend (:8000) + frontend (:3000)
```

- Chat UI: http://localhost:3000
- Agent queue UI: http://localhost:3000/agent
- API docs (OpenAPI): http://localhost:8000/docs
- Health: `curl http://localhost:8000/health` → `{"status":"ok", ...}`

## 6. Smoke test the chat

```bash
curl -s -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" -H "X-Customer-Id: demo-customer-1" \
  -d '{"message":"What is your return policy?"}'
# expect an approved-knowledge answer (intent: answer)
```

To exercise escalation and approval from the UI:

1. Ask something high-risk to trigger **escalation** (e.g. "sue"), then open
   `http://localhost:3000/agent` and mark it resolved.
2. Ask a state-changing action to trigger an **approval** (e.g. "cancel my
   subscription"), then open the agent view and Approve/Deny it.

## 7. Tests

```bash
# Backend
cd backend && PYTHONPATH=src uv run pytest -q

# MCP tool servers (run from each server dir so its pyproject pythonpath applies)
for s in knowledge-server support-data-server escalation-approval-server; do
  (cd "mcp-servers/$s" && uv run --project ../../backend python -m pytest tests -q)
done

# Lint
cd backend && uv run ruff check src tests
```

## 8. Golden evaluation (SC-001..SC-007)

```bash
# From repo root, backend running on :8000
uv run --project backend python eval/run_eval.py
# Worker-only variant (no HTTP server) for chat/knowledge cases:
PYTHONPATH=backend/src:. uv run --project backend python eval/run_eval.py --no-api
```

Reports pass rate, containment (escalation rate), and the SC-001..SC-007
measurement summary (incl. p95 chat latency, SC-007).

## 9. End-to-end UI smoke (Playwright) — optional

```bash
cd frontend
npm install
npx playwright install chromium
npm run e2e        # customer answer / escalation / approval-approve flows
```

## 10. Tear down

```bash
docker compose down          # stop services
docker compose down -v       # also drop the pgdata volume
```

> After running tests that drop/recreate tables, reseed knowledge (step 4) —
> the pytest fixture wipes seeded data per session (see runbook Troubleshooting).

## Env variables (documented in `.env.example`)

- `DATABASE_URL` — PostgreSQL connection string
- `SESSION_SECRET` — session signing secret (change from dev default for any
  non-localhost environment)
- `LLM_API_KEY` — API key for the Worker's LLM (Claude)
- `LLM_MODEL` — model tier