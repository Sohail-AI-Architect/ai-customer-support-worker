# Research: AI Customer Support Worker

**Phase 0 output** — resolves technical unknowns and the spec's deferred decisions
before design. Each item follows: **Decision / Rationale / Alternatives considered**.

## R1. Knowledge-base initial scope (deferred decision)

- **Decision**: Seed `knowledge_articles` with a starter set of common, low-risk
  FAQs: return policy, password-reset steps, shipping/order-status lookup,
  business hours, and a refund-policy reference. Admin-maintained; read-only to
  the Worker.
- **Rationale**: These are the highest-frequency, lowest-risk support questions,
  giving the MVP immediate containment value with a small, safely maintainable
  knowledge set. Approved-knowledge-only answering (FR-003/004) needs a real,
  seeded source of truth to evaluate against.
- **Alternatives considered**:
  - Empty knowledge base (build tooling first) — rejected: yields no containment
    and cannot be evaluated.
  - Large/vendor knowledge dump — rejected: over-scope for a learning project and
    harder to curate as "approved".

## R2. Tool-to-MCP mapping (deferred decision)

- **Decision**: Three MCP servers expose the six spec tools:
  - `knowledge-server` → `knowledge.search` (read-only).
  - `support-data-server` → `customer.info.get`, `ticket.get`, `ticket.list`,
    `ticket.create` (read/create only, session-scoped).
  - `escalation-approval-server` → `escalation.create`, `approval.request`
    (worker-initiated, audited).
- **Rationale**: Grouping by permission domain preserves least-privilege
  boundaries (knowledge is public to the Worker; customer/ticket data is
  session-scoped; escalations/approvals are write + audited) while keeping the
  server count small and learnable.
- **Alternatives considered**:
  - One monolithic MCP server exposing everything — rejected: blurs permission
    boundaries, contrary to least privilege.
  - One server per tool — rejected: over-fragmented for a learning project.

## R3. Escalation / approval UX (deferred decision)

- **Decision**: Human agents use a frontend **agent view** listing open
  escalations and pending approvals with context (conversation summary, reason,
  authorized data) and Approve/Reject actions. Customers see a "handed to a
  human" or "requires review" notice in the chat.
- **Rationale**: A simple list + decision UI is the smallest surface that lets
  humans fulfill the human-in-the-loop requirement without building a full
  support console.
- **Alternatives considered**:
  - Full support agent console — rejected: over-scope for MVP.
  - Approval via external chat/email — rejected: adds out-of-band complexity and
    hurts traceability.

## R4. Data retention (deferred decision)

- **Decision**: Data minimization plus defined retention: conversations/messages
  retained 90 days, worker action log 180 days, escalations/approvals retained as
  audit records (365 days). A scheduled cleanup job enforces these. Personal data
  is deleted on customer account deletion.
- **Rationale**: Balances the need for evaluation/replay and audit against
  privacy and storage cost (spec Section 11: defined retention).
- **Alternatives considered**:
  - Indefinite retention — rejected: fails data-minimization and privacy norms.
  - Minimal/no retention — rejected: undermines traceability and audit (NFR-007).

## R5. Worker determinism strategy (NFR-005)

- **Decision**: Combine deterministic intent rules with LLM tool-calling. A stable
  classifier (rule + LLM with fixed prompt) maps a message to an intent; skill and
  tool selection follow deterministic control flow. LLM temperature is fixed (0).
- **Rationale**: Yields reproducible behavior for evaluation while still using the
  model for understanding natural language (constitution Principle 3).
- **Alternatives considered**:
  - Pure rule-based classifier — rejected: too brittle for free-text support.
  - Pure LLM free-form — rejected: non-deterministic, hard to evaluate/contain.

## R6. LLM model choice

- **Decision**: Use Claude (via the Anthropic API) with tool use as the Worker's
  reasoning engine; the smallest sufficient model tier for the task, escalated
  only where needed (constitution Principle 8).
- **Rationale**: Strong tool-calling and instruction-following; aligns with the
  project's Claude Code tooling. Smallest-sufficient-model keeps cost and latency
  low for a learning project.
- **Alternatives considered**:
  - A local/smaller model — rejected for now: weaker tool-calling; can be revisited
    in a later experiment.

## R7. Persistence and migrations

- **Decision**: PostgreSQL with SQLAlchemy ORM and Alembic migrations, run as a
  release/startup step.
- **Rationale**: PostgreSQL is the project's specified store; ORM + migrations keep
  the schema versioned and reproducible (constitution Principle 12).
- **Alternatives considered**:
  - SQLite — rejected: not the project's specified store; weaker for concurrent
    chat sessions and deployments.

## R8. Testing and evaluation tooling

- **Decision**: pytest for backend/worker/contract tests; Vitest + Playwright for
  frontend; a custom `eval/` harness (golden set + graders) run in CI.
- **Rationale**: A deterministic grader harness is the core of evaluation-first
  development (constitution Principle 6); pytest/Vitest/Playwright are the
  standard, lowest-friction tools for the chosen stack.
- **Alternatives considered**:
  - A separate eval framework — rejected: a small custom harness over pytest is
    simpler and sufficient for ~20-30 golden cases.

## R9. Local development / containerization

- **Decision**: `docker-compose.yml` with `postgres`, `backend`, `frontend`; a
  `dev` profile with hot reload; backend packaged with `uv`.
- **Rationale**: One-command local stack matches the specified Docker Desktop +
  uv tooling and gives a reproducible learning environment (constitution
  Principle 12).
- **Alternatives considered**:
  - Local-only services without containers — rejected: less reproducible across
    machines and less representative of production.
