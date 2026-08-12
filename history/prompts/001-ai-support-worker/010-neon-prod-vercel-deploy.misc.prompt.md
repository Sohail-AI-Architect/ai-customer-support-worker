---
id: 010
title: Neon prod DB + Vercel deploy
stage: misc
date: 2026-08-12
surface: agent
model: oc/deepseek-v4-flash-free
feature: ai-support-worker
branch: main
user: Sarah Sohail
command: vercel --prod
labels: ["vercel", "neon", "postgres", "alembic", "deploy", "env"]
links:
  spec: specs/001-ai-support-worker/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - backend/serve.py (new Vercel python entrypoint wrapper; committed 170bf9d)
 - vercel.json (python build src -> backend/serve.py; committed 170bf9d)
 - backend/alembic -> migrations/ at repo root (existing) run against Neon
tests:
 - Neon pg version + CONNECT_OK via backend/.venv sqlalchemy
 - alembic upgrade head -> fc5f14a76542 (head); alembic check: no drift
 - seeds: 4 knowledge articles + demo-agent-1 user on Neon
 - vercel inspect: production Ready, both λ builds present
 - GET / (prod) -> 200; POST /api/chat -> 200 valid ChatResponse;
   GET /api/agent/escalations -> 200 []; Neon row counts grew (conversations=1, messages=2, escalations=1, customers=1, action_log=1)
---

## Prompt

Please configure the production Neon PostgreSQL database and deploy the project to Vercel:

1. Format the provided Neon connection string for SQLAlchemy/psycopg compatibility:
   DATABASE_URL="postgresql+psycopg://neondb_owner:npg_KPA5yG0DoMgx@ep-ancient-mouse-azqmyvnp-pooler.c-3.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

2. Set the following environment variables in Vercel for the production environment:
   - DATABASE_URL="postgresql+psycopg://neondb_owner:npg_KPA5yG0DoMgx@ep-ancient-mouse-azqmyvnp-pooler.c-3.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
   - ENVIRONMENT="production"
   - SESSION_SECRET="production-secure-session-key-2026"
   - KNOWLEDGE_SEED_PATH="data/knowledge_seed.json"

3. Run Alembic migrations locally against the Neon database URL to create all tables:
   'alembic upgrade head' (or 'python -m alembic upgrade head') using the Neon DATABASE_URL.

4. Execute seed scripts to populate initial knowledge base and agent data on Neon if available.

5. Trigger 'vercel --prod' to complete the production deployment and verify that frontend and backend API endpoints are working.

## Response snapshot

Formatted the string is already SQLAlchemy/psycopg compliant as given; used it
verbatim. Neon is reachable (PostgreSQL 18.4). Alembic migrations live at the
repo root (migrations/); `uv run --project backend alembic upgrade head`
applied `fc5f14a76542` -> head, `alembic check` clean. Seeded
`services.seed_knowledge` (4 articles) and `services.seed_demo` (demo-agent-1).

Set all four env vars in Vercel for Production via piped `vercel env add`
(DATABASE_URL, ENVIRONMENT, SESSION_SECRET, KNOWLEDGE_SEED_PATH) — all listed
as Sensitive. Then `vercel --prod` deployed Ready and roundtripped.

Debugging note: `/api/chat` first returned `FUNCTION_INVOCATION_FAILED`. Root
cause: Vercel's python runtime loads the entrypoint via
`spec_from_file_location` with the repo root (not backend/src) on sys.path, so
`from config import ...` / `from api import ...` failed (ModuleNameNotFound /
invocation crash). Confirmed by reading vercel-runtime `vc_init.py` +
`resolver.py` and reproducing locally ("No module named 'api'" with only the
root on path; OK with backend/src prepended). Fix: new `backend/serve.py`
wrapper prepends backend/src to sys.path and re-exports `app`; vercel.json
python build src switched to `backend/serve.py` (commit 170bf9d). Verified the
wrapper with a faithful spec_from_file_location('backend.serve', …) reproduction
(FastAPI app, 9 routes) and re-deployed.

## Outcome

- ✅ Impact: Production Neon DB provisioned (10 tables, 4 KB articles, demo
  agent) and Vercel prod deployment serving Next.js + FastAPI with full DB
  roundtrip; both frontend and backend endpoints verified working.
- 🧪 Tests: frontend `/` 200; `/api/chat` 200 (escalate fallback is by-design
  per test_escalation.py); `/api/agent/escalations` 200 []; Neon row counts
  increased post-deploy proving writes from the deployed function.
- 📁 Files: added `backend/serve.py`; `vercel.json` python build now
  `backend/serve.py`. Env vars stored in Vercel (not in repo).
- 🔁 Next prompts: consider `/health` on the frontend catch-all route (shadowed
  by Next.js); SSO Protection on the project may gate public API access — verify
  with the real frontend UI in a browser.
- 🧠 Reflection: Diagnosing FUNCTION_INVOCATION_FAILED required reading the VX
  python builder + vercel-runtime source rather than guessing; the minimal
  sys.path wrapper preserved the requested vercel.json routing and the local
  `PYTHONPATH=src` dev workflow.

## Evaluation notes (flywheel)

- Failure modes observed: no requirements.txt needed (uv.lock supported — build
  installed deps fine); python function crash at import due to repo-root
  sys.path; `vercel dev` unusable on Windows for this repro (dev-builder
  follows a different path); naive local harness clobbered stdlib sys.path and
  misled twice (fixed by mirroring runtime's prepend-only behavior).
- Graders run and results (PASS/FAIL): PASS — migration head, seeds, env vars,
  deploy Ready, backend+frontend endpoints verified, Neon writes confirmed.
- Prompt variant (if applicable): n/a.
- Next experiment (smallest change to try): none needed; if monorepo urls move,
  keep the wrapper's `Path(__file__).parent/"src"` relative logic.