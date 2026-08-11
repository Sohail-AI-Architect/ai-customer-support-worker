# AI Customer Support Worker (AI FDE Lab)

A Spec-Driven-Development learning project: a **Digital FTE / AI Customer
Support Worker** that answers common, low-risk support requests from approved
knowledge and authorized tools — and reliably escalates or requests human
approval for everything sensitive or high-risk.

Built end-to-end with the Spec-Driven Development method: constitution →
feature spec → architecture plan → tasks → TDD implementation → golden evaluation.

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