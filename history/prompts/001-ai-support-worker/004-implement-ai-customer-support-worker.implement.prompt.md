---
id: 004
title: Implement AI Customer Support Worker
stage: implement
date: 2026-08-09
surface: agent
model: oc/deepseek-v4-flash-free
feature: 001-ai-support-worker
branch: 001-ai-support-worker
user: Sarah Sohail
command: /sp.implement
labels: [ai-worker, customer-support, digital-fte, implementation, mvp, us1, tdd, evaluation-first]
links:
  spec: specs/001-ai-support-worker/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - .gitignore
  - .dockerignore
  - docker-compose.yml
  - backend/pyproject.toml
  - backend/src/config.py
  - backend/src/db.py
  - backend/src/main.py
  - backend/src/domain/authorization.py
  - backend/src/api/errors.py
  - backend/src/api/schemas.py
  - backend/src/api/deps.py
  - backend/src/api/chat.py
  - backend/src/models/customer.py
  - backend/src/models/user.py
  - backend/src/models/ticket.py
  - backend/src/models/conversation.py
  - backend/src/models/knowledge.py
  - backend/src/models/escalation.py
  - backend/src/models/approval.py
  - backend/src/models/action_log.py
  - backend/src/services/observability.py
  - backend/src/services/knowledge.py
  - backend/src/services/seed_knowledge.py
  - backend/src/worker/agent.py
  - backend/src/worker/skills/approved_knowledge_lookup.py
  - backend/src/worker/tools/registry.py
  - backend/data/knowledge_seed.json
  - backend/tests/conftest.py
  - backend/tests/unit/test_agent.py
  - backend/tests/contract/test_chat.py
  - backend/tests/integration/test_answer.py
  - eval/golden_set.json
  - eval/graders.py
  - eval/run_eval.py
  - specs/001-ai-support-worker/tasks.md
  - history/prompts/001-ai-support-worker/004-implement-ai-customer-support-worker.implement.prompt.md
tests:
  - 10 backend tests pass (unit, contract, integration) via `uv run pytest tests/`
  - US1 golden eval: 6/6 cases pass via eval/run_eval.py --no-api (containment 2/6)
---

## Prompt

/sp.implement invoked (empty args) to execute the approved implementation task
plan. Per the SpecifyPlus implement workflow: check prerequisites, verify
checklists, load tasks.md/plan.md, project setup (ignore files), parse tasks,
then execute phase-by-phase following TDD (tests written first and shown to
pass/fail), marking each completed task as [X] in tasks.md, and create a PHR.

The AI Customer Support Worker (Digital FTE) learning project: build a Worker
that answers common low-risk support questions from approved knowledge and
recognizes when to escalate to a human. Phase 1 Setup + Phase 2 Foundational +
Phase 3 US1 MVP are in scope for this run, following the 63-task plan.

## Response snapshot

Executed implementation through US1 MVP core:

- **Setup/ignore files**: Created .gitignore (secrets, Python/uv, Node/TS,
  Docker, editors), .dockerignore, docker-compose.yml (postgres:16, backend,
  frontend services).
- **Foundational backend**: config (pydantic-settings, DB URL, LLM settings),
  SQLAlchemy 2.0 session (db.py, Base), 9 ORM models (customer, user, ticket,
  conversation+message, knowledge, escalation, approval, action_log), hybrid
  authorization (WorkerPermissions, ensure_customer_scope, ensure_ticket_action_allowed),
  structured logging + trace_id (observability.py), API error envelope
  (errors.py), tool registry, WorkerAgent orchestrator with intent classification
  and HIGH_RISK_KEYWORDS.
- **US1 core**: knowledge service + seed script + data/knowledge_seed.json (4
  articles), approved_knowledge_lookup skill (injectable for tests), POST
  /api/chat endpoint (scope → invoke Worker → persist messages + action log),
  API schemas + customer/agent deps, FastAPI main with lifespan + trace_id
  middleware + exception handlers.
- **Tests (TDD, all green)**: unit (agent intent/refusal/escalation), contract
  (POST /api/chat shape, headers, validation), integration (answer from approved
  knowledge, refuse when no match, escalate sensitive request) — 10 passed.
- **Eval harness**: eval/golden_set.json (6 US1 cases), eval/graders.py,
  eval/run_eval.py. Initial run 3/6 — the evaluation-first loop caught two real
  precision bugs in knowledge matching (first-token-only match; stop-word false
  positive on "the"). Fixed via relevance scoring + stop-word filter →
  **6/6 eval pass**, containment 2/6 (33%).
- **tasks.md**: marked T014-T018, T020-T023, T025 as [X]. Left open: T019 (MCP
  knowledge-server), T024 (chat UI), plus Phases 4-8.

## Outcome

- ✅ Impact: Working, compiling US1 MVP backend that answers from approved
  knowledge, refuses/fabricates-never, escalates high-risk requests, and
  persists every exchange + audit action with trace_id. Tests and eval harness
  verify behavior end-to-end. Evaluation-first surfaced and fixed real matching
  precision bugs.
- 🧪 Tests: 10/10 backend tests pass; US1 golden eval 6/6 pass.
- 📁 Files: 30+ files created across backend/src, backend/tests, eval/,
  docker-compose.yml, ignore files; tasks.md updated.
- 🔁 Next prompts: complete US1 remaining (T019 MCP server, T024 chat UI), then
  Phases 4-8 (US2-US5, Polish); containerize backend/frontend; Alembic migration.
- 🧠 Reflection: Evaluation-first development is the strongest guardrail — the
  golden eval caught a false-positive matching bug that unit tests would have
  missed. Keep the eval harness as the arbiter for all later user stories.

## Evaluation notes (flywheel)

- Failure modes observed: knowledge.search only matched the first query token
  (common-word false positives, e.g. "what"); no confidence threshold caused a
  refusal case to answer with an unrelated article; stop-word "the" (len 3)
  matched unrelated articles. All surfaced by the eval harness, not unit tests.
- Graders run and results (PASS/FAIL): US1 golden eval 3/6 → 6/6 PASS after
  relevance-scoring + stop-word fixes. Containment 2/6 (33%).
- Prompt variant (if applicable): /sp.implement with empty args, executing
  tasks.md plan phase-by-phase with TDD.
- Next experiment (smallest change to try): apply the same eval-first feedback
  loop to US2 (authorized retrieval + cross-customer refusal) by adding golden
  retrieval/refusal cases before implementing the ticket endpoints.
