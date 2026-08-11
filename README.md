# AI Customer Support Worker (AI FDE Lab)

A Spec-Driven-Development learning project: a **Digital FTE / AI Customer
Support Worker** that answers common, low-risk support requests from approved
knowledge and authorized tools — and reliably escalates or requests human
approval for everything sensitive or high-risk.

Built end-to-end with the Spec-Driven Development method: constitution →
feature spec → architecture plan → tasks → TDD implementation → golden evaluation.

## 🚀 Quick Access & Local Testing Routes

Once the stack is running (see [Run & test locally](#run--test-locally)), open
these in your browser:

| Route | URL | What it's for |
|---|---|---|
| **Customer Chat UI** | [http://localhost:3000/chat](http://localhost:3000/chat) | Test **knowledge-base answers**, ticket retrieval, and escalations from the customer side |
| **Agent Dashboard UI** | [http://localhost:3000/agent](http://localhost:3000/agent) | Manage **human escalations** and **approval gates** |
| **Backend API Docs (Swagger)** | [http://localhost:8000/docs](http://localhost:8000/docs) | Explore every REST endpoint interactively |
| **Health Check Endpoint** | [http://localhost:8000/health](http://localhost:8000/health) | Verify the backend is up (`{"status":"ok", ...}`) |

## Run & test locally

Clone the repo, then from the root:

```bash
# 1. Environment
cp .env.example .env            # git-ignored; edit SESSION_SECRET for non-local

# 2. Start the full stack (Postgres + backend + frontend)
docker compose up -d

# 3. Apply database migrations
uv run --project backend alembic upgrade head

# 4. Seed demo data (approved knowledge + demo agent for the agent queue)
cd backend
PYTHONPATH=src uv run python -m services.seed_knowledge
PYTHONPATH=src uv run python -m services.seed_demo
cd ..
```

Now open the routes above. Sample test prompts:

- **Knowledge-base query** → in the chat UI, ask *"What is your return policy?"* or
  *"What are your business hours?"* — you get an approved answer (no badge).
- **Escalation** → ask *"I want to request a refund."* — the reply shows an
  **escalated to human** badge; approve it in the agent dashboard.
- **Sensitive human approval** → ask *"Can you cancel my subscription?"* — the
  reply states it needs human approval and is **held, not executed**; then
  **Approve**/**Deny** it in the agent dashboard.
- **Raw API** → `curl http://localhost:8000/health`, or use the Swagger UI at
  [http://localhost:8000/docs](http://localhost:8000/docs).

> **Prerequisites:** Docker Desktop running, `uv` (Python), and `node`/`npm`.
> A full first-run walkthrough lives in
> [`specs/001-ai-support-worker/quickstart.md`](specs/001-ai-support-worker/quickstart.md).

## What it does

- **Answers common questions** from an approved knowledge base — never fabricates
  (SC-003).
- **Retrieves a customer's own account/ticket info**, session-scoped — never
  another customer's data (SC-005).
- **Creates support tickets** — create + read only; cannot update, close, or
  delete (FR-010).
- **Escalates ambiguous/unsupported/high-risk requests** to a human agent with
  context (FR-013).
- **Holds sensitive/state-changing actions** behind a human **approval gate** —
  never executes them before a decision (FR-014/015; SC-006).

## Design pillars

- **Deterministic where possible**: intent classification is rule-based and
  evaluable (NFR-005), not an opaque model bolt-on.
- **Least privilege**: every data read is session-scoped; every write is a
  bounded create/propose. Secrets never hardcoded (NFR-003).
- **Human in the loop**: escalation and approval are distinct, audited flows.
- **Evaluated continuously**: a golden eval set grades containment and each
  success criterion (SC-001..SC-007).

## Stack

- **Backend** — FastAPI + SQLAlchemy 2.0 + Alembic + PostgreSQL 16 (`backend/`)
- **MCP tool servers** — knowledge / support-data / escalation-approval
  (`mcp-servers/`)
- **Frontend** — Next.js (App Router) customer chat + agent queue (`frontend/`)
- **Tests & quality** — pytest, ruff, Playwright; golden eval harness (`eval/`)

## Quick start

See [`specs/001-ai-support-worker/quickstart.md`](specs/001-ai-support-worker/quickstart.md)
for the first-run, end-to-end walkthrough (Postgres → migrate → seed → run →
test → eval).

## Documentation

- Operations runbook: [`docs/runbook.md`](docs/runbook.md)
- API usage: [`docs/api.md`](docs/api.md)
- Architecture: [`docs/architecture.md`](docs/architecture.md)
- Security hardening review: [`docs/security-review.md`](docs/security-review.md)
- Feature spec / plan / tasks: `specs/001-ai-support-worker/`
- ADRs: `history/adr/`

## Governing principles

The project is governed by its ratified constitution
([`.specify/memory/constitution.md`](.specify/memory/constitution.md)). All
implementation follows the Spec-Driven Development workflow under
[`CLAUDE.md`](CLAUDE.md), which records every prompt in
[`history/prompts/`](history/prompts/).