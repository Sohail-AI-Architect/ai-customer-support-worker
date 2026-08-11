---
id: 003
title: Tasks AI Customer Support Worker
stage: tasks
date: 2026-08-09
surface: agent
model: oc/deepseek-v4-flash-free
feature: 001-ai-support-worker
branch: 001-ai-support-worker
user: Sarah Sohail
command: /sp.tasks
labels: [ai-worker, customer-support, digital-fte, tasks, task-generation, spec-driven-development]
links:
  spec: specs/001-ai-support-worker/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-ai-support-worker/tasks.md
  - history/prompts/001-ai-support-worker/003-tasks-ai-customer-support-worker.tasks.prompt.md
tests:
  - (task list includes test tasks; red-green within each story — T017/T018, T026/T027, T034/T035, T042/T043, T050/T051, plus E2E T060)
---

## Prompt

/sp.tasks invoked on the approved AI Customer Support Worker feature. (Command
arguments were empty; tasks were generated from the design documents in
specs/001-ai-support-worker/: plan.md, spec.md, research.md, data-model.md,
contracts/, quickstart.md.)

Generate implementation tasks organized by user story following the SpecifyPlus
tasks template: Phase 1 Setup, Phase 2 Foundational (blocking), one phase per
user story in priority order (US1 P1, US2 P2, US3 P3, US4 P4, US5 P4), and a final
Polish & cross-cutting phase. Each task must follow the checklist format
`- [ ] [TaskID] [P?] [Story?] Description with file path`. Include exact file
paths, dependency/execution order, parallel execution examples, and an MVP-first
implementation strategy. Tests are included because the spec explicitly requires
evaluation-first development with tests written and shown to fail before
implementation (spec Section 15, plan Section 24).

## Response snapshot

Generated `specs/001-ai-support-worker/tasks.md` with 63 tasks across 8 phases,
organized by user story for independent implementation and testing:

- Phase 1 Setup (7): monorepo scaffold, backend uv init, frontend Next.js init,
  linting, .env.example/.gitignore, docker-compose skeleton, Alembic scaffold.
- Phase 2 Foundational (9): SQLAlchemy models (9 entities), config/DB session,
  initial migration, session auth + hybrid authorization helpers, structured
  logging + trace_id, MCP server skeleton + tool registry, knowledge seed script,
  eval harness skeleton, API error envelope.
- Phase 3 US1 (9, MVP): /api/chat contract+integration tests, knowledge.search
  tool, knowledge service, approved_knowledge_lookup skill, Worker agent core,
  POST /api/chat, chat UI, golden answering eval cases.
- Phase 4 US2 (8): ticket GET contract+authz tests, customer.info/ticket tools,
  customer_context skill, session scoping, GET /api/tickets, chat ticket info,
  golden retrieval/refusal cases.
- Phase 5 US3 (8): ticket create tests, ticket.create tool, ticket_handling skill,
  no update/close/delete enforcement, POST /api/tickets, ticket confirmation UI,
  golden creation cases.
- Phase 6 US4 (8): escalation tests, escalation.create tool, escalation_triage
  skill, escalation model/service, agent escalation endpoints + UI, golden
  escalation cases.
- Phase 7 US5 (8): approval tests, approval.request tool, approval model/service,
  approval_protocol skill, approval decision endpoint + UI, golden approval cases.
- Phase 8 Polish (6): full eval run, containerization, Playwright E2E, security
  hardening review, docs/runbook, quickstart end-to-end validation.

Includes Dependencies & Execution Order, per-story parallel examples, and
Implementation Strategy (MVP = US1, incremental delivery, parallel team strategy).
Each task uses the required checklist format with IDs, [P]/[Story] markers, and
exact file paths.

## Outcome

- ✅ Impact: Produced an immediately executable task list derived from the
  approved plan/spec, enabling independent user-story implementation with
  red-green test discipline and an MVP-first strategy.
- 🧪 Tests: Test tasks are part of the task list (written-first red-green within
  each story); not executed yet.
- 📁 Files: specs/001-ai-support-worker/tasks.md created; PHR created.
- 🔁 Next prompts: /sp.implement to execute the tasks (starting with Setup +
  Foundational, then US1 MVP).
- 🧠 Reflection: Commands are ready for an implementation agent with no additional
  context — every task names its file paths and dependencies. Tests were included
  because the spec mandates evaluation-first/red-green.

## Evaluation notes (flywheel)

- Failure modes observed: none in generation. Prior scripts (create-new-feature,
  update-agent-context) showed Windows PowerShell 5.1 vs pwsh7 differences.
- Graders run and results (PASS/FAIL): N/A (task generation). Format validation:
  all tasks follow `- [ ] [ID] [P?] [Story?] Description + file path`.
- Prompt variant (if applicable): /sp.tasks with empty args, generating from
  design docs.
- Next experiment (smallest change to try): Begin /sp.implement on Phase 1 Setup
  and Phase 2 Foundational.
