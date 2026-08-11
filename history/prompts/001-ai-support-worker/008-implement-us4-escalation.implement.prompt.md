---
id: 008
title: Implement US4 escalation
stage: implement
date: 2026-08-09
surface: agent
model: oc/deepseek-v4-flash-free
feature: 001-ai-support-worker
branch: 001-ai-support-worker
user: Sarah Sohail
command: /sp.implement (Phase 6: US4)
labels: [ai-worker, customer-support, digital-fte, us4, escalation, human-in-the-loop, tdd, worker-initiated, audited]
links:
  spec: specs/001-ai-support-worker/spec.md
  ticket: null
  adr: history/adr/002-ticket-operations-model.md
  pr: null
files:
  - backend/src/services/escalations.py
  - backend/src/services/escalation_approval.py
  - backend/src/worker/skills/escalation_triage.py
  - backend/src/api/agent_escalations.py
  - backend/src/api/chat.py
  - backend/src/api/deps.py
  - backend/src/main.py
  - backend/tests/integration/test_escalation.py
  - backend/tests/contract/test_agent_escalations.py
  - backend/tests/unit/test_escalation_triage.py
  - mcp-servers/escalation-approval-server/pyproject.toml
  - mcp-servers/escalation-approval-server/src/escalation_approval_server.py
  - mcp-servers/escalation-approval-server/tests/test_escalation_approval_server.py
  - frontend/src/app/agent/page.tsx
  - frontend/src/app/agent/AgentClient.tsx
  - frontend/src/app/globals.css
  - eval/golden_set.json
  - eval/run_eval.py
  - specs/001-ai-support-worker/tasks.md
tests:
  - backend/tests/integration/test_escalation.py (T042, 3 passed)
  - backend/tests/contract/test_agent_escalations.py (T043, 6 passed)
  - backend/tests/unit/test_escalation_triage.py (T045, 2 passed)
  - mcp-servers/escalation-approval-server/tests (T044, 4 passed)
  - Full backend suite: 48 passed; ruff clean
  - mcp-servers: knowledge 4, support-data 8, escalation-approval 4
  - Golden eval (API mode): 12/12 passed, containment 4/12 (33%)
---

## Prompt

Continue the /sp.implement workflow for the AI Customer Support Worker. Phase 5
(US3 ticket creation) was verified (eval 10/10). Execute Phase 6: User Story 4 —
Recognize and escalate tricky requests (P4). Implement tasks T042-T049 per
specs/001-ai-support-worker/tasks.md following TDD. Requirements: when the Worker
detects an ambiguous, unsupported, sensitive, or high-risk request, it escalates
to a human instead of answering/acting (never guesses), persists an Escalation
record with context linked to the conversation, and a human agent can see it in
an agent queue and mark it resolved. Enforce session scoping (cross-customer
escalation refused) and worker-initiated, audited escalation.

## Response snapshot

Completed Phase 6 (US4) via TDD, all T042-T049 marked [X] in tasks.md.

- T042 integration test: chat high-risk/unsupported → escalated AND an open
  Escalation persisted. Red (no persistence) → wired chat.py → 3 green.
- T043 contract test GET/POST /api/agent/escalations: required header, agent
  role, list shape, resolve. Red (endpoints absent) → 5 green (+1 username test).
- T046 escalations service (create/list/resolve) + T044 escalation-approval MCP
  server (escalation.create, session-scoped, cross-customer refused) → 4 green.
- T045 escalation_triage skill wrapping escalation.create → 2 green.
- Wired the skill into the real path: chat.py persists escalation via
  EscalationTriageSkill over a backend-local EscalationApprovalServer adapter.
- T047 agent_escalations.py endpoints + router registration; require_agent
  accepts id OR username (found & fixed a real bug: non-UUID username caused a
  UUID type error before the username fallback ran).
- T048 agent UI (/agent) lists open escalations with context + Mark resolved;
  builds. Added seed_demo.py for a demo agent.
- T049 golden cases US4-001/002 (escalate + persist) + runner/grader → 12/12.

Full API-mode golden eval: 12/12 (US1 6, US2 2, US3 2, US4 2); containment 4/12
(33%). Full backend 48 passed; mcp-servers 16 passed; ruff clean.

## Outcome

- ✅ Impact: Added the human-in-the-loop safety path end-to-end — Worker
  escalates tricky requests into a persisted, audited Escalation queue that a
  human agent views and resolves, with session scoping enforced (cross-customer
  escalation refused).
- 🧪 Tests: 48 backend + 16 mcp-server tests pass; golden eval 12/12 API mode.
- 📁 Files: 22 source/test/config files (see files: above).
- 🔁 Next prompts: Phase 7 — US5 human approval for sensitive actions
  (T050-T057); then Phase 8 polish (T058-T063).
- 🧠 Reflection: TDD caught a real require_agent bug — the id-then-username
  fallback raised a UUID type error for usernames because the id query ran on an
  invalid UUID string before the fallback; restructured to branch on parse
  success.

## Evaluation notes (flywheel)

- Failure modes observed: no escalation persisted before wiring; require_agent
  UUID error on username; fixed usernames collided across tests sharing the DB
  (now uuid-based); missing X-User-Id gives 422 not 403 (test corrected).
- Graders run and results (PASS/FAIL): US1 6/6, US2 2/2, US3 2/2, US4 2/2 — all
  PASS.
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Move to US5 (human approval) per plan.
