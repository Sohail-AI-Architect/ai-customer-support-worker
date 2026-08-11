# Pull Request Description

## Title

`feat: implement AI Customer Support Worker end-to-end (US1-US5, Phase1-8)`

## Summary

Implements the **AI Customer Support Digital FTE / Worker** via Spec-Driven
Development (constitution → spec → plan → tasks → TDD → evaluation). The Worker
answers common, low-risk requests from an **approved knowledge base** using
**authorized tools**, and reliably **escalates** or holds for **human approval**
anything ambiguous, sensitive, or high-risk. It never fabricates answers, never
accesses another customer's data, and can only **create + read** tickets.

## What changed

- **Spec & design** (`specs/001-ai-support-worker/`): `spec.md` (FR-001..017,
  NFRs, SC-001..007), `plan.md`, `tasks.md`, `data-model.md`,
  `contracts/openapi.yaml`, `contracts/mcp-tools.md`, `research.md`,
  `quickstart.md`.
- **Backend** (`backend/`): FastAPI + SQLAlchemy 2.0 + PostgreSQL 16 + Alembic.
  Deterministic-intent Worker (`answer / retrieve / create_ticket / escalate /
  approval / out_of_scope`), skills for knowledge lookup / customer context /
  ticket handling / escalation triage / approval protocol. Hybrid authorization
  (session scoping + role-bounded tools). APIs: `/api/chat`, `/api/tickets`
  (create + read-only), `/api/agent/escalations`, `/api/agent/approvals`.
  **61 tests passing.**
- **MCP tool servers** (`mcp-servers/`): `knowledge-server`,
  `support-data-server`, `escalation-approval-server` — read-only or
  bounded-create tools only (`knowledge.search`, `customer.info.get`,
  `ticket.get/list/create`, `escalation.create`, `approval.request`).
  **20 tests passing.**
- **Frontend** (`frontend/`): Next.js customer chat + agent queue (escalations
  resolve, approvals approve/deny). Playwright e2e specs (chat answer,
  escalation resolve, approval approve) + a `globalSetup` that resets worker
  state so the suite is deterministic against the shared dev DB.
- **Evaluation** (`eval/`): golden set (14 cases, US1–US5) + harness grading
  pass rate, containment, and SC-001..SC-007 (incl. p95 latency).
- **Docs & records**: `README.md`, `docs/` (runbook, api, architecture,
  security-review), `history/adr/` (001–003), full PHR history.

## Task status — 63/63 complete

| Phase | Scope | Done | Open |
|-------|-------|------|------|
| 1 | Setup (shared infra) | 7 | 0 |
| 2 | Foundational (blocking prereqs) | 9 | 0 |
| 3 | US1 — Answer common questions (P1, MVP) | 9 | 0 |
| 4 | US2 — Retrieve authorized customer/ticket info | 8 | 0 |
| 5 | US3 — Create a support ticket | 8 | 0 |
| 6 | US4 — Recognize & escalate tricky requests | 8 | 0 |
| 7 | US5 — Human approval for sensitive actions | 8 | 0 |
| 8 | Polish & cross-cutting concerns | 6 | 0 |
| **Total** | | **63** | **0** |

## Verification

- Golden eval **14/14 passed**: SC-001 resolution 71% (≥70%), SC-006 approval
  2/2 gated (100%), SC-007 p95 ~77ms–2.5s (≪15s). Containment 29%.
- Backend **61 passed**, ruff clean; MCP **20 passed**.
- Quickstart validated end-to-end (migrate → seed → compose build/up → chat
  smoke → tests → eval).
- Security hardening review passed (`docs/security-review.md`): secrets
  excluded, least privilege, no update/close/delete tickets.
- **Playwright e2e 3/3 passed** (chat answer, escalation resolve, approval
  approve). Three fixes were required to green it: frontend `BACKEND_URL` now
  points at the `backend` compose service (Next proxy was hitting the container's
  own localhost), the demo agent is re-seeded after pytest wipes tables, and a
  Playwright `globalSetup` truncates worker state so the suite is deterministic.

## Notes / deferred

- MCP stdio/HTTP transport bridge to the backend is the remaining wiring
  (servers consumed via in-process adapters today); documented in
  `backend/src/mcp/__init__.py`.
