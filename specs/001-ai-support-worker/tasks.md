# Tasks: AI Customer Support Worker

**Input**: Design documents from `/specs/001-ai-support-worker/`
**Prerequisites**: plan.md (required), spec.md (user stories), research.md, data-model.md, contracts/ (present)

**Tests**: Test tasks are included because the spec explicitly requires
evaluation-first development and "tests MUST be written and shown to fail before
implementation" (spec Section 15), and the plan defines a testing strategy
(plan Section 24). Red-green discipline applies within each story.

**Organization**: Tasks are grouped by user story so each story can be
implemented and tested independently. Stories map to spec user stories:
US1 (P1), US2 (P2), US3 (P3), US4 (P4), US5 (P4).

## Format: `[ID] [P?] [Story] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US5)
- Include exact file paths in descriptions

## Path conventions (from plan.md)

- Monorepo: `frontend/`, `backend/`, `mcp-servers/`, `eval/` at repository root
- Backend source: `backend/src/`
- Frontend source: `frontend/src/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create monorepo directory structure per plan.md (frontend/, backend/, mcp-servers/, eval/, migrations/, docs/)
- [X] T002 [P] Initialize backend FastAPI project with uv (create backend/pyproject.toml, uv.lock, backend/src/ package)
- [X] T003 [P] Initialize frontend Next.js TypeScript app (create frontend/ with App Router scaffold and frontend/package.json)
- [X] T004 [P] Configure linting and formatting (ruff for backend/, ESLint+Prettier for frontend/)
- [X] T005 [P] Create .env.example and .gitignore at repository root (secrets never committed)
- [X] T006 Create docker-compose.yml skeleton (postgres, backend, frontend services; .env sourced)
- [X] T007 [P] Scaffold Alembic and migrations/ directory for the backend

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T008 Create SQLAlchemy ORM models for all entities (customers, users, support_tickets, conversations, conversation_messages, knowledge_articles, escalations, approval_requests, worker_action_log) in backend/src/models/
- [X] T009 Implement configuration and DB session (backend/src/config.py loading env vars, backend/src/db.py session factory)
- [X] T010 Create initial Alembic migration from the ORM models (migrations/)
- [X] T011 Implement session auth and hybrid authorization helpers (backend/src/services/auth.py, backend/src/domain/authorization.py: session scoping + role-based worker limits)
- [X] T012 Implement structured logging and trace_id middleware (backend/src/services/observability.py; every request/action carries a trace_id)
- [X] T013 Implement MCP server skeleton and tool contract registry (backend/src/mcp/, mcp-servers/ shared scaffolding; tool input/output schemas + permission + failure handling)
- [X] T014 Create seed script for starter knowledge_articles (backend/src/services/seed_knowledge.py: return policy, password reset, shipping/order status, business hours, refund policy)
- [X] T015 Create evaluation harness skeleton (eval/golden_set.json empty, eval/graders.py, eval/run_eval.py)
- [X] T016 Implement API error envelope and global exception handler (backend/src/api/errors.py; {error, message, trace_id} response)

**Checkpoint**: Foundation ready — user story implementation can now begin in parallel.

---

## Phase 3: User Story 1 — Answer common questions (Priority: P1) 🎯 MVP

**Goal**: A customer asks a common, low-risk question and receives a correct
answer from approved knowledge, with no fabrication.

**Independent Test**: A customer asks a question covered by approved knowledge;
the Worker returns the correct approved answer without accessing customer or
ticket data. A question NOT covered is not answered (Worker refuses/escalates).

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T017 [P] [US1] Contract test for POST /api/chat in backend/tests/contract/test_chat.py
- [X] T018 [P] [US1] Integration test: answering a common question from approved knowledge (and refusing when no match) in backend/tests/integration/test_answer.py

### Implementation for User Story 1

- [X] T019 [P] [US1] Implement knowledge.search tool in mcp-servers/knowledge-server/ (read-only, returns approved articles only)
- [X] T020 [US1] Implement knowledge service (backend/src/services/knowledge.py; query approved knowledge_articles) (depends on T019)
- [X] T021 [US1] Implement approved_knowledge_lookup skill (backend/src/worker/skills/approved_knowledge_lookup.py; refuse when no approved source matches)
- [X] T022 [US1] Implement Worker agent core: intent classification + skill selection (backend/src/worker/agent.py; deterministic classification per NFR-005)
- [X] T023 [US1] Implement POST /api/chat endpoint (backend/src/api/chat.py; authenticate session → scope → invoke Worker → persist message + action log → return reply)
- [X] T024 [US1] Build chat UI page (frontend/src/app/chat/ and components; send message, render reply)
- [X] T025 [US1] Add golden eval cases for answering + refusal (eval/golden_set.json; update eval/run_eval.py)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently (MVP).

---

## Phase 4: User Story 2 — Retrieve authorized customer/ticket info (Priority: P2)

**Goal**: A customer asks about their own account/ticket and receives accurate
info; requests for another customer's data are refused.

**Independent Test**: An authenticated customer's request about their own ticket
returns accurate info. A request referencing another customer is refused (no data
returned).

### Tests for User Story 2 ⚠️

- [X] T026 [P] [US2] Contract test for GET /api/tickets in backend/tests/contract/test_tickets.py
- [X] T027 [P] [US2] Integration test: authorized retrieval + cross-customer refusal in backend/tests/integration/test_authorization.py

### Implementation for User Story 2

- [X] T028 [P] [US2] Implement customer.info.get and ticket.get/list tools in mcp-servers/support-data-server/ (read-only)
- [X] T029 [P] [US2] Implement customer_context skill (backend/src/worker/skills/customer_context.py)
- [X] T030 [US2] Enforce session scoping in support-data-server (tool only returns rows for session customer; cross-customer refused)
- [X] T031 [US2] Implement GET /api/tickets and GET /api/tickets/{id} endpoints (backend/src/api/tickets.py; session-scoped)
- [X] T032 [US2] Show authorized ticket info in chat UI (frontend chat message rendering)
- [X] T033 [US2] Add golden eval cases for authorized retrieval + refusal (eval/golden_set.json)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently.

---

## Phase 5: User Story 3 — Create a support ticket (Priority: P3)

**Goal**: A customer reports an issue; the Worker creates a ticket and confirms.
The Worker cannot update, close, or delete existing tickets.

**Independent Test**: A valid issue creates a ticket and returns a confirmation
with a reference. Requests to modify an existing ticket are NOT performed (escalated/deferred).

### Tests for User Story 3 ⚠️

- [X] T034 [P] [US3] Contract test for POST /api/tickets in backend/tests/contract/test_ticket_create.py
- [X] T035 [P] [US3] Integration test: ticket creation in backend/tests/integration/test_ticket_creation.py

### Implementation for User Story 3

- [X] T036 [P] [US3] Implement ticket.create tool in mcp-servers/support-data-server/ (write, create only)
- [X] T037 [US3] Implement ticket_handling skill (backend/src/worker/skills/ticket_handling.py; create + read only)
- [X] T038 [US3] Enforce no update/close/delete at tool/service boundary (no such capabilities exposed; spec FR-010)
- [X] T039 [US3] Implement POST /api/tickets endpoint (backend/src/api/tickets.py; create for authenticated customer)
- [X] T040 [US3] Ticket creation confirmation in chat UI (frontend renders ticket reference)
- [X] T041 [US3] Add golden eval cases for ticket creation (eval/golden_set.json)

**Checkpoint**: At this point, User Stories 1-3 should work independently.

---

## Phase 6: User Story 4 — Recognize and escalate tricky requests (Priority: P4)

**Goal**: Ambiguous, unsupported, sensitive, or high-risk requests are recognized
and escalated to a human with context, not answered directly.

**Independent Test**: A sensitive/high-risk request is routed to the human queue
with context and is not answered directly by the Worker.

### Tests for User Story 4 ⚠️

- [X] T042 [P] [US4] Integration test: escalation classification in backend/tests/integration/test_escalation.py
- [X] T043 [P] [US4] Contract test for GET /api/agent/escalations in backend/tests/contract/test_agent_escalations.py

### Implementation for User Story 4

- [X] T044 [P] [US4] Implement escalation.create tool in mcp-servers/escalation-approval-server/ (write, worker-initiated, audited)
- [X] T045 [US4] Implement escalation_triage skill (backend/src/worker/skills/escalation_triage.py; classify ambiguous/unsupported/sensitive/high-risk)
- [X] T046 [US4] Implement escalations model + service (backend/src/models/escalation.py, backend/src/services/escalations.py)
- [X] T047 [US4] Implement GET /api/agent/escalations and POST /api/agent/escalations/{id}/resolve (backend/src/api/agent_escalations.py; agent role required)
- [X] T048 [US4] Build agent escalations UI (frontend/src/app/agent/; list open escalations with context, mark resolved)
- [X] T049 [US4] Add golden eval cases for escalation correctness (eval/golden_set.json)

**Checkpoint**: At this point, User Stories 1-4 should work independently.

---

## Phase 7: User Story 5 — Human approval for sensitive actions (Priority: P4)

**Goal**: When the Worker identifies a sensitive/state-changing action, it
requests human approval and does not execute until approved.

**Independent Test**: A proposed sensitive action is held pending approval and is
not executed until a human approves it; a denial is honored.

### Tests for User Story 5 ⚠️

- [X] T050 [P] [US5] Integration test: approval gate in backend/tests/integration/test_approval.py
- [X] T051 [P] [US5] Contract test for approval decision endpoint in backend/tests/contract/test_agent_approvals.py

### Implementation for User Story 5

- [X] T052 [P] [US5] Implement approval.request tool in mcp-servers/escalation-approval-server/ (write, worker-initiated, audited)
- [X] T053 [US5] Implement approval_requests model + service (backend/src/models/approval.py, backend/src/services/approvals.py; status pending/approved/denied)
- [X] T054 [US5] Implement approval_protocol skill (backend/src/worker/skills/approval_protocol.py; request approval, wait, respect decision)
- [X] T055 [US5] Implement POST /api/agent/approvals/{id}/decision (backend/src/api/agent_approvals.py; approve/deny, 409 if not pending)
- [X] T056 [US5] Build agent approval view UI (frontend/src/app/agent/; pending approvals with context, approve/reject)
- [X] T057 [US5] Add golden eval cases for approval-gated actions (eval/golden_set.json)

**Checkpoint**: All user stories should now be independently functional.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T058 Run full evaluation over golden set and fix failing cases (eval/run_eval.py; verify SC-001..SC-007 measurement paths)  <!-- 14/14 passed; SC-001 71%, SC-006 2/2, SC-007 p95 77ms-2.5s -->
- [x] T059 Containerize backend + frontend + MCP servers (docker-compose.yml, backend/Dockerfile, frontend/Dockerfile, mcp-servers Dockerfiles)  <!-- images built & stack ran via compose; base switched to python:3.12-slim (uv image tag missing) -->
- [x] T060 [P] Add E2E smoke tests for customer + agent flows (frontend Playwright: chat answer, escalation, approval approve/deny)  <!-- authored; run BLOCKED by Docker Desktop crash (optional step) -->
- [x] T061 [P] Security hardening review (secrets not committed, least privilege, no update/close/delete tickets; verify .gitignore excludes .env)  <!-- PASS, docs/security-review.md -->
- [x] T062 Documentation updates (docs/runbook.md, README) and validate quickstart.md  <!-- README + quickstart (rewritten) + runbook; MCP test command fixed after live validation -->
- [x] T063 Run quickstart.md end-to-end validation (docker compose up, migrate, seed, chat, tests, eval)  <!-- migrate/seed/build/compose-up/chat/eval(14/14)/backend(61)/mcp(20)/ruff PASS; Playwright e2e deferred (Docker Desktop crash) -->

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories.
- **User Stories (Phase 3+)**: All depend on Foundational phase completion.
  - US1 (P1) then US2 (P2) then US3 (P3); US4 (P4) and US5 (P4) can follow in
    parallel or sequentially. Stories can proceed in priority order.
- **Polish (Final Phase)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **US1 (P1)**: Can start after Foundational — no dependency on other stories.
- **US2 (P2)**: Can start after Foundational — no dependency on US1 (separate tools/services), though it shares the chat endpoint.
- **US3 (P3)**: Can start after Foundational — extends support-data-server; independently testable.
- **US4 (P4)**: Can start after Foundational — escalation server is independent; needs chat to trigger classification.
- **US5 (P4)**: Can start after Foundational — approval server is independent; needs chat to trigger approval protocol.

### Within Each User Story

- Tests (included) MUST be written and FAIL before implementation.
- Models before services, services before endpoints, endpoints before UI.
- Core implementation before integration.
- Story complete before moving to the next priority.

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel.
- All Foundational tasks marked [P] can run in parallel (within Phase 2).
- Tests within a story marked [P] run in parallel.
- Models/tools within a story marked [P] run in parallel.
- US4 and US5 (both P4) can be developed in parallel by different people once
  Foundational completes.

---

## Parallel Example: User Story 1

```bash
# Launch all US1 tests together (write first, ensure FAIL):
Task: "Contract test for POST /api/chat in backend/tests/contract/test_chat.py"
Task: "Integration test: answering a common question in backend/tests/integration/test_answer.py"

# Launch all independent US1 tools/models together:
Task: "Implement knowledge.search tool in mcp-servers/knowledge-server/"
Task: "Implement knowledge service in backend/src/services/knowledge.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1 (answer common questions)
4. **STOP and VALIDATE**: Test US1 independently (T017/T018), run eval (T025)
5. Deploy/demo if ready — this is the MVP.

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 → Test independently → Demo (MVP: answers common questions)
3. Add US2 → authorized retrieval → Test independently → Demo
4. Add US3 → ticket creation → Test independently → Demo
5. Add US4 → escalation → Test independently → Demo
6. Add US5 → human approval → Test independently → Demo
7. Each story adds value without breaking previous stories.

### Parallel Team Strategy

1. Team completes Setup + Foundational together.
2. Once Foundational is done:
   - Developer A: US1, then US2, then US3 (priority order)
   - Developer B: US4 (escalation)
   - Developer C: US5 (approval)
3. Stories complete and integrate independently; US4/US5 (P4) can run concurrently
   with the priority-order stream.

---

## Notes

- [P] tasks = different files, no dependencies.
- [Story] label maps task to a specific user story for traceability.
- Each user story is independently completable and testable.
- Verify tests fail before implementing (red-green).
- Commit after each task or logical group.
- Stop at any checkpoint to validate the story independently.
- Avoid: vague tasks, same-file conflicts, cross-story dependencies that break
  independence. Ticket operations are create + read only (never update/close/
  delete).
