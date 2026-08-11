---
id: 001
title: US5 Human Approval Gate
stage: green
date: 2026-08-10
surface: agent
model: oc/deepseek-v4-flash-free
feature: ai-support-worker
branch: 001-ai-support-worker
user: Sarah Sohail
command: /sp.implement
labels: ["approval", "human-in-the-loop", "us5", "tdd", "worker-skill"]
links:
  spec: specs/001-ai-support-worker/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - backend/src/services/approvals.py (new: create/list/decide approval requests)
 - backend/src/services/escalation_approval.py (add approval.request adapter + scope)
 - backend/src/worker/skills/approval_protocol.py (new skill: propose + request approval)
 - backend/src/worker/agent.py (add Intent.APPROVE, APPROVAL_ACTIONS, _handle_approval)
 - backend/src/api/chat.py (persist approval_requests on approval_required)
 - backend/src/api/agent_approvals.py (new: GET list + POST decision, 409 if not pending)
 - backend/src/api/schemas.py (add ApprovalDecisionRequest)
 - backend/src/main.py (register agent_approvals router)
 - backend/tests/integration/test_approval.py (new: approval gate)
 - backend/tests/contract/test_agent_approvals.py (new: decision endpoint)
 - backend/tests/unit/test_agent.py (add state-change approval case)
 - backend/tests/unit/test_approval_protocol.py (new skill unit test)
 - mcp-servers/escalation-approval-server/src/escalation_approval_server.py (add approval.request tool)
 - mcp-servers/escalation-approval-server/tests/test_escalation_approval_server.py (add tool tests)
 - frontend/src/app/agent/AgentClient.tsx (approvals list + approve/deny)
 - frontend/src/app/globals.css (approval badge + approve/deny buttons)
 - eval/golden_set.json (add US5-001/002 approval cases)
 - eval/run_eval.py (add approval runner + grader)
 - specs/001-ai-support-worker/tasks.md (mark T050-T057 [X])
tests:
 - backend suite: 61 passed
 - mcp escalation-approval server: 8 passed
 - golden eval (live server): 14/14 passed, containment 4/14 (29%)
 - ruff check src tests: all checks passed
---

## Prompt

/sp.implement (empty args) — continue the implementation plan from Phase6 (US4
escalation complete) into Phase7: User Story 5, human approval for sensitive
actions (T050-T057). The docs/ and migrations/ work from the prior turn was
reported complete. This invocation proceeds to implement US5 following TDD:
approval gate for sensitive/state-changing actions held pending human approval,
with create+read-only no-execute-until-approved semantics (plan Section 14,
spec FR-014/FR-015). The user's convert-to-approval instruction also required
confirming the plan, constitution, spec, and project structure before the work.

## Response snapshot

Implemented the US5 human-approval gate end-to-end:

- **Model/service**: `services/approvals.py` — create_approval_request (pending),
  list_pending_approvals, decide_approval (approved/denied; LookupError on
  missing, ValueError 409 if no longer pending). The approval_requests model already
  existed; the initial migration already creates the table, so no new migration.

- **Tool layer**: added `approval.request` to mcp-servers/escalation-approval-server
  and the backend-local EscalationApprovalServer adapter, both session-scoped
  (refuse cross-customer) and worker-initiated/audited.

- **Agent**: added `Intent.APPROVE` ("approval") with APPROVAL_ACTIONS
  (cancel/delete/close/refund state-changers) checked BEFORE HIGH_RISK so e.g.
  "cancel my account" gates approval rather than escalating; the agent flags
  approval_required=True; chat.py persists the approval via ApprovalProtocolSkill.

- **API**: GET /api/agent/approvals (pending list) + POST
  /api/agent/approvals/{id}/decision (approved/denied, 409 if not pending),
  agent role required.

- **Frontend**: agent queue now shows pending approvals with Approve/Deny plus
  the existing escalations.

- **Eval**: US5-001/002 approval cases + run_approval_case/grade_approval_case.

- **Tests**: red confirmed before implementation (9 failed/1 passed via 404 + no
  approval rows), then all green (backend 61, mcp 8, eval 14/14).

Note: started with Postgres down (Docker Desktop stopped) — connection-timeout
errors, resolved by launching Docker Desktop and `docker compose up -d postgres`.
Database then needed `alembic stamp head` (test fixture recreates tables, wiping
the version), after which `alembic check` reports no drift.

## Outcome

- ✅ Impact: Sensitive/irreversible actions are now gated behind human approval
  (FR-014/015, SC-006). Introduces a new intent ("approval") to the classifier
  and a pending-approval lifecycle; the decision is audited (decided_by/at).
  Minimal viable change; no update/close/delete surfaces added (create+read only
  preserved).
- 🧪 Tests: backend 61 passed; mcp 8 passed; golden eval 14/14 (containment 29%);
  ruff clean in enforced scope.
- 📁 Files: 19 files touched (see front-matter files list).
- 🔁 Next prompts: Phase8 Polish T058-T063 (full eval re-run, containerization,
  Playwright E2E, security review, docs+quickstart validation). The docs/ and
  migrations/ work is complete.
- 🧠 Reflection: The prior US1 unit test asserted "cancel my account" escalated;
  US5 legitimately re-routs state-changing actions to approval, so the test was
  updated to use a purely high-risk message ("request a refund") and a new
  state-change approval case was added. This is a spec-driven behavior change,
  not a regression.

## Evaluation notes (flywheel)

- Failure modes observed: (1) test run confused DB-down connection timeouts with
  real test failures — resolved by starting Postgres first; (2) pytest collection
  choked running all three mcp-server test dirs in one command (path quirk) —
  run each dir individually; (3) shared dev DB lost its alembic_version after
  test-table recreate — fixed with `alembic stamp head`.
- Graders run and results (PASS/FAIL): eval 14/14 PASS; backend 61 PASS; mcp 8 PASS.
- Prompt variant (if applicable): TDD red→green, followed the established
  escalation pattern (agent flags → chat.py persists via session-scoped skill).
- Next experiment (smallest change to try): full golden-eval re-run across all
  stories after Phase8, and Playwright E2E for the approval approve/deny flow.