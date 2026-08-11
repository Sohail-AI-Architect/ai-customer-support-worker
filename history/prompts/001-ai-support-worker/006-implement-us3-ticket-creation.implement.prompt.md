---
id: 006
title: Implement US3 ticket creation
stage: implement
date: 2026-08-09
surface: agent
model: oc/deepseek-v4-flash-free
feature: 001-ai-support-worker
branch: 001-ai-support-worker
user: Sarah Sohail
command: continue /sp.implement (Phase 5: US3)
labels: [ai-worker, customer-support, digital-fte, us3, ticket-creation, tdd, create-only, fr-010, fr-011]
links:
  spec: specs/001-ai-support-worker/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/worker/agent.py
  - backend/src/worker/skills/ticket_handling.py
  - backend/src/services/customer_data.py
  - backend/src/api/tickets.py
  - backend/src/api/schemas.py
  - backend/src/api/chat.py
  - backend/tests/contract/test_ticket_create.py
  - backend/tests/integration/test_ticket_creation.py
  - backend/tests/integration/test_chat_create.py
  - backend/tests/unit/test_agent.py
  - mcp-servers/support-data-server/src/support_data_server.py
  - mcp-servers/support-data-server/tests/test_support_data_server.py
  - frontend/src/app/chat/ChatClient.tsx
  - frontend/src/app/globals.css
  - eval/golden_set.json
  - eval/run_eval.py
  - specs/001-ai-support-worker/tasks.md
tests:
  - backend/tests/contract/test_ticket_create.py (T034, 3 passed)
  - backend/tests/integration/test_ticket_creation.py (T035, 3 passed)
  - backend/tests/integration/test_chat_create.py (2 passed)
  - backend/tests/unit/test_agent.py (10 passed)
  - mcp-servers/support-data-server/tests (T036, 8 passed)
  - mcp-servers/knowledge-server/tests (4 passed)
  - Full backend suite: 37 passed; ruff clean
  - Golden eval (API mode): 10/10 passed, containment 2/10 (20%)
---

## Prompt

Continue the /sp.implement workflow for the AI Customer Support Worker. Phase 4 (US2 authorized retrieval) was verified (no-api US1 6/6 green; API-mode 8/8 green). Execute Phase 5: User Story 3 — Create a support ticket (P3). Implement tasks T034-T041 per specs/001-ai-support-worker/tasks.md following TDD (write the contract/integration test first, show it fail, then implement, show it pass). Requirements: a customer reporting an issue gets a ticket created and a confirmation with a ticket reference (FR-009); the Worker MUST NOT update, close, or delete existing tickets (FR-010, create+read only); requests to modify an existing ticket are escalated/deferred to a human, never honored (FR-011). Enforce session scoping (no cross-customer data) and no update/close/delete capability at the tool and service boundaries.

## Response snapshot

Completed Phase 5 (US3) via TDD, all T034-T041 marked [X] in tasks.md.

- T034 contract test POST /api/tickets → 405 red → implemented schema + endpoint → 3 green.
- T035 integration test (renamed to test_ticket_creation.py to avoid basename collision with the contract test) → fixed cross-customer assertion to accept 403/404 refusal, removed JSON body from DELETE request → 3 green.
- T036 ticket.create tool in support-data-server → red (unknown_tool) → added ToolSpec + `_ticket_create`; made params optional so missing subject yields a `validation_error` ToolFailure instead of a TypeError → 8 green (incl. session-required + subject-required).
- T037 TicketHandlingSkill wraps `ticket.create` returning safe `TicketCreateResult`; wired into WorkerAgent with a new `Intent.CREATE_TICKET` and CREATE_TICKET_KEYWORDS + MODIFY_TICKET_KEYWORDS. FR-011 modify requests escalate with reason `ticket_modify`. Default skill is None so the agent refuses (`no_ticket_skill`) rather than guess.
- T038 enforced create+read-only at both API and tool layers; integration test asserts PATCH/PUT/DELETE return 405.
- T039 POST /api/tickets (201) for the authenticated customer; added `ticket.create` to the backend-local CustomerDataServer (was missing → caused chat create to escalate).
- T040 frontend ChatClient renders intent and a "ticket created" badge + `.created` badge style; build succeeds.
- T041 added golden cases US3-001 (create → 201/open) and US3-002 (create cross-customer isolation) and runner/grader support in eval/run_eval.py.

Full API-mode golden eval: 10/10 passed (US1 6, US2 2, US3 2); containment 2/10 (20%). Full backend suite 37 passed; support-data-server 8 passed; knowledge-server 4 passed; ruff clean.

## Outcome

- ✅ Impact: Added the Worker's first authorized write action (create-only ticket creation) end-to-end — chat → intent classify → ticket_handling skill → session-scoped ticket.create tool → API → persisted row → chat confirmation with a ticket reference. Enforced create+read-only (FR-010) and escalate-on-modify (FR-011) at both the service and tool boundaries.
- 🧪 Tests: 37 backend + 8 support-data-server + 4 knowledge-server pass; golden eval 10/10 API mode.
- 📁 Files: 15 source/test/config files (see files: above).
- 🔁 Next prompts: Phase 6 — US4 recognize and escalate tricky requests (T042-T049); then Phase 7 US5 human approval (T050-T057); then Phase 8 polish (T058-T063).
- 🧠 Reflection: TDD caught two real issues — (1) the backend-local CustomerDataServer lacked ticket.create, so chat creation silently escalated; (2) defaulting TicketHandlingSkill(db) would have broken the no-skill refusal, so it correctly defaults to None.

## Evaluation notes (flywheel)

- Failure modes observed: 405 instead of 201 (endpoint absent); cross-customer GET returns 403 not 404 (refusal, test expected 404); TestClient.delete() rejects a body; duplicate test basename collection error; missing-subject TypeError before validation; knowledge reseed needed after conftest DB wipe.
- Graders run and results (PASS/FAIL): US1 6/6, US2 2/2, US3 2/2 — all PASS.
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Move to US4 (escalation) per plan; no agent prompt experiment required.
