# Implementation Plan: AI Customer Support Worker

**Branch**: `001-ai-support-worker` | **Date**: 2026-08-09 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-ai-support-worker/spec.md`

> This plan defines **HOW** the system will be built. It is governed by the
> ratified constitution v1.0.0 and aligned to the approved spec. It does not
> contain implementation code; that is produced by `/sp.tasks` and `/sp.implement`.

## Summary

Build a web-based **AI Customer Support Worker** — a Digital FTE / AI Worker
that resolves common, low-risk customer requests from an approved knowledge base
using authorized tools, and escalates or requires human approval for ambiguous,
sensitive, or high-risk cases. It is a learning project demonstrating the AI FDE /
Agent Factory approach end-to-end: a Next.js chat UI, a FastAPI backend, a
Python-based AI Worker that orchestrates skills and MCP-exposed tools against
PostgreSQL, with evaluation-first verification and full traceability.

## Technical Context

**Language/Version**: Python 3.11+ (backend + AI Worker), TypeScript (frontend)  
**Primary Dependencies**: FastAPI, Next.js (App Router), PostgreSQL, an LLM with
tool-calling (Claude via the Anthropic API), `uv` for env/package management  
**Storage**: PostgreSQL (conversations, messages, tickets, customers, knowledge,
escalations, approvals, worker action log)  
**Testing**: pytest (backend/worker), pytest + Playwright or Vitest (frontend),
contract tests, and an evaluation harness over a golden test set  
**Target Platform**: Local via Docker Desktop (docker-compose); deployed as
containerized web app (frontend + backend API + worker)  
**Project Type**: web (frontend + backend + worker + db) — multi-component monorepo  
**Performance Goals**: chat reply perceived within ~15s p95 (NFR-001); sufficient
for a small-team learning scale  
**Constraints**: create + read ticket ops only (no update/close/delete); Worker
never fabricates answers; least-privilege and hybrid authorization; every action
logged and traceable  
**Scale/Scope**: small/learning — a handful of concurrent chat sessions, a seeded
starter knowledge base, single default language, chat channel only

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The plan satisfies the ratified constitution v1.0.0:

- **1. Spec-Driven Development** ✅ — Plan is derived from the approved spec; tasks
  will be derived from this plan in a later phase.
- **2. Outcome-First** ✅ — Success metrics (SC-001..SC-007) and acceptance
  criteria from the spec drive the design and evaluation architecture.
- **3. Digital FTE / AI Worker Architecture** ✅ — Worker is deterministic-where-
  possible, bounded, and evaluated; responsibilities from spec Section 7.
- **4. Reusable Skills** ✅ — Skill architecture packages domain knowledge +
  operational instructions as reusable modules.
- **5. Tools & MCP** ✅ — Every tool has boundaries, permissions, I/O, and failure
  handling; exposed via MCP servers (Section 8 below).
- **6. Evaluation-First** ✅ — Golden set + graders + containment metric defined
  before implementation.
- **7. Human-in-the-Loop** ✅ — Escalation and approval flows gate sensitive or
  high-risk actions.
- **8. AI Safety & Governance** ✅ — Irreversible actions require approval; Worker
  stays within authorization boundary.
- **9. Security & Least-Privilege** ✅ — Hybrid authz, session scoping, role-based
  worker limits, no secrets in code.
- **10. Testing & Verification** ✅ — Automated testing strategy covers unit,
  integration, contract, and evaluation.
- **11. Observability & Traceability** ✅ — Worker action log + structured logs +
  trace IDs.
- **12. Production Readiness** ✅ — Dockerized, env-config, migration, documented
  runbook.
- **13. Maintainable Code** ✅ — Smallest viable multi-component structure; no
  premature abstraction.
- **14. Separation of Concerns** ✅ — Spec/Plan/Tasks/Implementation/Evaluation
  kept distinct.

**Gates: PASS.** The multi-component web structure (frontend + backend + worker +
db) is inherent to the feature (a chat UI calling an agent API), not accidental
complexity. See **Complexity Tracking** below.

## Project Structure

### Documentation (this feature)

```text
specs/001-ai-support-worker/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── openapi.yaml     # API contract (REST)
│   └── mcp-tools.md     # Tool-to-MCP contract mapping
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

The plan uses a **monorepo** with a single web-app structure (frontend + backend),
because the feature is inherently a web application (customer chat UI + agent
API). The AI Worker lives inside the backend as a Python package.

```text
ai-fde-lab/
├── frontend/                        # Next.js (TypeScript) chat UI
│   ├── src/
│   │   ├── app/                     # App Router routes (chat page, agent views)
│   │   ├── components/              # Chat UI, ticket list, escalation/approval views
│   │   └── lib/                     # API client, auth/session helpers
│   └── tests/                       # Component/UI tests
├── backend/                         # FastAPI + AI Worker (Python 3.11)
│   ├── src/
│   │   ├── api/                     # REST routes (chat, tickets, auth, agent views)
│   │   ├── worker/                  # AI Customer Support Worker agent
│   │   │   ├── agent.py             # Worker orchestrator (classify → skill → respond)
│   │   │   ├── skills/              # Reusable skill modules (one per skill)
│   │   │   ├── tools/               # Tool definitions + tool-use helpers
│   │   │   └── state.py             # Conversation/session state handling
│   │   ├── domain/                  # Domain logic, authorization, approval gates
│   │   ├── models/                  # SQLAlchemy ORM models (PostgreSQL)
│   │   ├── services/                # Knowledge, tickets, auth, observability
│   │   ├── mcp/                     # MCP server definitions (tool servers)
│   │   └── config.py                # Settings, secrets loading
│   └── tests/
│       ├── unit/
│       ├── integration/
│       └── contract/
├── mcp-servers/                     # Standalone MCP tool servers (if split out)
│   ├── knowledge-server/
│   ├── support-data-server/
│   └── escalation-approval-server/
├── eval/                            # Evaluation harness + golden test set
│   ├── golden_set.json              # Representative requests + expected outcomes
│   ├── graders.py                   # Correctness / containment / escalation graders
│   └── run_eval.py
├── docker-compose.yml               # postgres + backend + frontend
├── .env.example                     # Env var template (no secrets)
├── migrations/                      # Alembic DB migrations
└── docs/                            # Runbooks, architecture notes
```

**Structure Decision**: A web-app monorepo (`frontend/` + `backend/`) is selected.
The AI Worker is a first-class Python package within `backend/src/worker` because
it is tightly coupled to backend domain logic, auth, and PostgreSQL. MCP tool
servers are placed under `mcp-servers/` (standalone processes) to honor
least-privilege and independent deployability. `eval/` is a top-level directory so
evaluation is a first-class, testable artifact (constitution Principle 6).

## 1. Overall System Architecture

A **3-tier web application** with an integrated AI agent:

- **Frontend** (Next.js): customer chat UI + human-agent views (escalations,
  approvals). Serves as the client; calls the backend API over HTTP(S).
- **Backend API** (FastAPI): authentication/authorization, chat endpoint, ticket
  endpoints, knowledge endpoints, agent-facing endpoints (escalation/approval
  review). Owns all business rules and persistence.
- **AI Worker** (Python): the Digital FTE. Receives a chat message, classifies
  intent, selects a skill, invokes tools (via MCP), builds a response, and
  decides when to escalate or request approval.
- **PostgreSQL**: single source of truth (conversations, messages, tickets,
  customers, knowledge, escalations, approvals, action log).
- **MCP tool servers**: bounded, permissioned interfaces the Worker uses to act
  on knowledge, customer data, tickets, and approvals.

The Worker never talks to PostgreSQL directly; it goes through MCP-exposed tools,
which are themselves thin, authorized service calls. This enforces least privilege
and a single contract surface.

## 2. Repository / Folder Structure

Monorepo as shown in **Project Structure**. Key boundaries:
- `frontend/` — Next.js app (customer + agent surfaces).
- `backend/` — FastAPI API + AI Worker + domain + persistence.
- `mcp-servers/` — standalone MCP tool servers.
- `eval/` — golden set + graders + evaluation runner.
- `migrations/`, `docker-compose.yml`, `.env.example`, `docs/` at repo root.

## 3. Frontend Architecture

Next.js (App Router) with TypeScript.

- **Customer chat page** (`/chat`): streaming/async message send and response
  display; renders worker responses, ticket confirmations, and "handed to a human"
  notices.
- **Agent views** (`/agent`): authenticated human-agent surfaces listing open
  escalations and pending approvals, with context (conversation summary, reason,
  authorized data) and Approve/Reject actions.
- **API client layer** (`src/lib`): typed calls to backend endpoints; session/auth
  handling.
- **State**: React state per page; conversation history fetched from backend (the
  backend is the source of truth, not the browser).
- **Testing**: component tests (Vitest) and end-to-end smoke tests (Playwright)
  for the customer flow.

The frontend is deliberately thin — no business logic; it renders backend and
Worker results.

## 4. FastAPI Backend Architecture

FastAPI provides REST endpoints and hosts the Worker invocation path.

- **API layer** (`src/api`): route modules for auth, chat, tickets, knowledge,
  escalations, approvals. Request validation via Pydantic models.
- **Domain layer** (`src/domain`): authorization checks, approval-gate logic,
  ticket-op rules (create + read only).
- **Services** (`src/services`): knowledge lookup, ticket service, auth service,
  observability.
- **Persistence** (`src/models`): SQLAlchemy ORM models; Alembic for migrations.
- **Chat endpoint flow**: receive message → authenticate session → scope to
  customer → invoke Worker → persist message/action → return response (and any
  escalation/approval state).

## 5. AI Customer Support Worker Architecture

The Worker is a deterministic-where-possible Python agent that orchestrates
skills and tools:

1. **Intent classification**: classify the message into an intent (answer /
  retrieve / create_ticket / escalate / out_of_scope) and detect ambiguity,
  sensitivity, or risk. Rule- and LLM-assisted, but **stable for a given input**
  (NFR-005).
2. **Skill selection**: choose the skill that handles the intent (approved
  knowledge lookup, customer context, ticket handling, escalation triage,
  approval protocol).
3. **Tool invocation**: the skill calls one or more tools through the MCP layer,
  each gated by authorization.
4. **Response building**: produce a customer-facing answer from approved
  knowledge or tool results — never fabricated.
5. **Decision**: resolve, escalate, or request approval, per the flow below.

The Worker is **stateless across calls**; all context is loaded from persisted
conversation state (Section 16), making behavior reconstructable and evaluable.
The Worker emits a structured decision/action record for every step.

## 6. Skill Architecture

Skills are reusable Python modules packaging domain knowledge + operational
instructions (constitution Principle 4). Each skill declares, in a manifest:

- **name**, **inputs**, **outputs**, **when-it-applies** (conditions),
  **permissions required**, and a deterministic execution function.

Skills (from spec Section 8):

- **approved_knowledge_lookup** — retrieve/apply the approved answer; refuse when
  no approved source matches.
- **customer_context** — read authorized customer info for the authenticated
  customer only.
- **ticket_handling** — look up and create tickets (read + create only).
- **escalation_triage** — classify ambiguous/unsupported/sensitive/high-risk and
  prepare an escalation with context.
- **approval_protocol** — propose a sensitive action, request approval, and
  respect the decision.

Skills call tools via the MCP layer; they do not touch PostgreSQL directly.

## 7. Tool Architecture

Tools are the Worker's bounded actions (constitution Principle 5). Each tool has a
declared contract: input schema, output schema, permission scope, and failure
behavior. Tools map 1:1 to the spec's Section 9 tools:

| Spec tool | Tool (impl) | Permission | Side effects |
|-----------|-------------|------------|--------------|
| Knowledge retrieval | `knowledge.search` | read-only, always allowed | none |
| Customer info | `customer.info.get` | read-only, scoped to session customer | none |
| Ticket lookup | `ticket.get` / `ticket.list` | read-only, scoped | none |
| Ticket creation | `ticket.create` | write, create only | inserts a ticket row |
| Escalation | `escalation.create` | write, worker-initiated | inserts escalation row |
| Approval request | `approval.request` | write, worker-initiated | inserts approval row |

Failure behavior: tools return a structured error result (never raise out of
bounds); the Worker fails safely — it does not guess and escalates on tool failure.

## 8. MCP Integration and Tool-to-MCP Mapping

MCP servers provide the standardized, permissioned surface for the Worker to
discover and call tools (spec Section 10). Concrete mapping (deferred decision
resolved here):

- **`knowledge-server`** (MCP) → exposes `knowledge.search` from the approved
  knowledge base. Read-only.
- **`support-data-server`** (MCP) → exposes `customer.info.get`, `ticket.get`,
  `ticket.list`, `ticket.create`. Enforces session scoping + role-based limits
  (no update/close/delete). Read/create only.
- **`escalation-approval-server`** (MCP) → exposes `escalation.create` and
  `approval.request`. Write, worker-initiated, audited.

Servers are separate processes under `mcp-servers/` to honor least privilege and
independent deployability. The Worker accesses them over the MCP protocol; the
backend authorizes each request before a server acts.

## 9. PostgreSQL Data Model

Detailed schema in `data-model.md`. Core tables:

- **customers** — id, identity, name, status.
- **users** — internal users incl. human agents/admin (for auth roles).
- **support_tickets** — id, customer_id, subject, description, status, created_at.
- **conversations** — id, customer_id, channel, started_at, status.
- **conversation_messages** — id, conversation_id, role (customer/worker/system),
  content, created_at.
- **knowledge_articles** — id, question, answer, keywords, status (approved),
  updated_at.
- **escalations** — id, conversation_id, reason, context, status
  (open/assigned/resolved), handled_by, created_at.
- **approval_requests** — id, conversation_id, proposed_action, payload,
  status (pending/approved/denied), decided_by, decided_at.
- **worker_action_log** — id, trace_id, conversation_id, action, tool, input
  hash, outcome, created_at (observability).

## 10. API Boundaries and Request/Response Flow

REST API (OpenAPI contract in `contracts/openapi.yaml`). Public endpoints:

- `POST /api/auth/login` — start a customer session.
- `GET /api/auth/session` — current session/scoping.
- `POST /api/chat` — send a message; returns worker response + any
  escalation/approval state.
- `GET /api/tickets` — list the authenticated customer's tickets.
- `GET /api/tickets/{id}` — get one of the customer's tickets.
- `POST /api/tickets` — create a ticket (used by Worker via tool; may also be
  exposed to customer).

Agent-facing endpoints (require agent role):

- `GET /api/agent/escalations` — list open escalations.
- `POST /api/agent/escalations/{id}/resolve` — mark handled.
- `GET /api/agent/approvals` — list pending approvals.
- `POST /api/agent/approvals/{id}/decision` — approve/deny.

Request/response flow (Section "Request Flow" below).

## 11. Authentication and Authorization Design

Hybrid model (per user decision and spec Section 13):

- **Customer session**: Next.js initiates a session (cookie/JWT). The backend
  authenticates the session and **scopes all data access to that customer**
  (session scoping). Customer data and ticket endpoints only return rows for the
  authenticated customer.
- **Agent/admin session**: human agents and administrators authenticate with a
  role (agent/admin) to access escalation and approval surfaces.

## 12. Hybrid Authorization (session scoping + worker roles)

- **Session scoping**: any customer-scoped read (customer info, tickets) is
  filtered by the authenticated customer id at the service/tool layer. It is
  impossible for the Worker to address another customer.
- **Role-based Worker permissions**: the Worker operates as a role with a fixed
  permission set — read approved knowledge; read/create tickets (never
  update/close/delete); read customer info (scoped); initiate escalations and
  approvals. These limits are enforced in the MCP tool layer, not just in the
  prompt.
- Both checks must pass; a tool call is authorized only if the session scope and
  the Worker's role both permit it.

## 13. Ticket Operations

- **Read**: `ticket.get` / `ticket.list` — only for the authenticated customer.
- **Create**: `ticket.create` — creates a new ticket; returns a reference.
- **No update/close/delete**: the ticket MCP server and service **do not expose**
  update/close/delete capabilities. Any customer request to modify an existing
  ticket is escalated or defers to a human (spec FR-011).

## 14. Human Approval and Escalation Architecture

Two related flows, both persisted and audited:

- **Escalation**: when the Worker detects an ambiguous, unsupported, sensitive,
  or high-risk request (or a tool failure it cannot resolve), it creates an
  `escalations` record with context (conversation summary, reason, relevant
  authorized data) and informs the customer they are being handed to a human.
  Human agents see it in the agent view and resolve it.
- **Approval**: when the Worker identifies a sensitive/state-changing action it is
  permitted to propose, it creates an `approval_requests` record with
  `status=pending` and **does not act**. A human agent approves or denies; the
  Worker proceeds only on approval, and the outcome is recorded for audit. Denials
  are honored and the customer is informed appropriately.

## 15. Approved Knowledge-Base Design

- **Source of truth**: `knowledge_articles` table, seeded with a **starter set**
  (deferred decision resolved): common low-risk FAQs — return policy, password
  reset steps, shipping/order status lookup, business hours, and refund-policy
  reference. Admin-maintained; read-only to the Worker.
- **Lookup**: `knowledge.search` returns an approved article; the Worker answers
  from it verbatim/paraphrased. If no article matches, the Worker MUST NOT guess —
  it says it cannot answer and/or escalates (FR-004/005).

## 16. AI Worker State / Session Handling

- **Persistence of truth**: conversations and messages are stored in PostgreSQL,
  not the browser. Each chat session maps to a `conversations` row; messages are
  appended to `conversation_messages`.
- **Stateless Worker**: the Worker is invoked per message with the loaded
  conversation history as context. This makes behavior reconstructable,
  testable, and traceable, and supports multi-session concurrency.
- **Trace**: each message/action carries a `trace_id` linking the Worker action
  log, escalation/approval records, and response.

## 17. Error Handling and Failure Recovery

- **Tool failure**: tools return structured errors; the Worker fails safely — no
  guessing, escalate or state it cannot complete the request.
- **Dependency failure** (DB / MCP server / LLM): the API returns a graceful,
  user-friendly error and logs the trace; the Worker does not fabricate.
- **Retry/backoff**: bounded retries for transient tool calls; no infinite loops.
- **Observability**: every error is logged with trace_id for diagnosis.

## 18. Security and Least-Privilege Design

- Least-privilege tool surface (Section 7/12); no update/close/delete tickets.
- Session scoping + role-based worker limits enforced at the tool/service layer.
- Secrets never in code (see Section 19).
- Audit: `worker_action_log` records every action and data access.
- Input validation (Pydantic) and authorization checks on every endpoint.

## 19. Secrets and Environment Configuration

- `.env.example` at repo root documents required env vars **without values**.
- Real secrets (DB credentials, LLM API key, session secret) come from `.env`
  (git-ignored) and/or the container environment — never committed.
- `backend/src/config.py` loads settings from environment via `uv`/dotenv.
- `.gitignore` excludes `.env` and secrets.

## 20. Logging, Observability, and Traceability

- Structured JSON logs from backend and Worker.
- `worker_action_log` table: every action, tool call, decision, and data access,
  keyed by `trace_id`.
- Escalation/approval records are audit objects.
- A `trace_id` propagates from request through Worker, tools, and DB writes,
  enabling end-to-end replay and audit (constitution Principle 11, NFR-004/007).

## 21. Evaluation Architecture

Evaluation is first-class (constitution Principle 6):

- `eval/golden_set.json` — representative customer requests with expected
  outcomes (correct answer / correct escalation / correct refusal / correct
  approval flow).
- `eval/graders.py` — deterministic graders for correctness, appropriateness,
  escalation accuracy, refusal behavior, and containment.
- `eval/run_eval.py` — runs the Worker over the golden set and produces a scored
  report.
- Evaluations MUST pass before implementation is complete; evals are written and
  shown to fail before implementation (red-green discipline).

## 22. Golden Test Set and Grader Strategy

- **Golden set**: ~20–30 representative requests covering each user journey:
  common questions (answer), no-match questions (refuse/escalate), authorized
  ticket status (retrieve), ticket creation, sensitive/high-risk (escalate),
  approval-gated actions, out-of-scope/abusive.
- **Graders**: each case has an expected outcome and acceptance predicate; graders
  assert the Worker's classification, whether it used approved knowledge, whether
  it stayed in scope, whether it escalated/approval-gated correctly, and whether it
  ever fabricated.

## 23. Containment Metric

- **Containment rate** = (in-scope low-risk requests resolved by the Worker
  without a human) / (total in-scope low-risk requests).
- Target: ≥ 70% (SC-001). Computed by the eval runner over the golden set and
  measured in operation via the action log (request → resolved vs escalated).
- Escalation precision (SC-004) and zero-fabrication (SC-003) are graded
  alongside.

## 24. Automated Testing Strategy

- **Unit**: skill logic, tool contracts, authorization rules, approval gates.
- **Integration**: FastAPI endpoints → Worker → MCP tools → PostgreSQL
  (real/containerized DB).
- **Contract**: OpenAPI contract validation; MCP tool contract tests.
- **Evaluation**: golden-set harness (Section 22) run in CI.
- **Frontend**: component tests (Vitest) + E2E smoke (Playwright) for customer
  flow and agent approval/denial.
- Every functional requirement maps to a test (NFR-006).

## 25. Docker / Local Development Architecture

- `docker-compose.yml`: services **postgres**, **backend** (FastAPI + Worker +
  MCP servers), **frontend** (Next.js). A `dev` profile runs with hot reload.
- Backend packaged with `uv`; `uv.lock` pins dependencies.
- DB migrations applied on backend startup/CI.
- `.env` sourced by compose; `.env.example` documents variables.
- Local: `docker compose up` starts the full stack; quickstart in `quickstart.md`.

## 26. Deployment Considerations

- Containerized deployment of the three services behind a reverse proxy/TLS.
- Managed PostgreSQL or a managed Postgres-compatible service for persistence.
- Secrets injected via the environment/secrets manager; DB migrations run as a
  release step.
- Observability: structured logs + action log shipped to a log store; trace IDs
  for replay.
- Learning scope: full production deployment is a later concern; this plan
  targets a reproducible local Docker deployment with a documented runbook.

## Request Flow (customer → answer)

```text
Customer
  → Next.js Chat UI            (POST /api/chat)
  → FastAPI                    (authenticate session → scope to customer → load state)
  → AI Customer Support Worker (classify intent → select skill)
  → Skills                     (approved_knowledge_lookup / customer_context / ticket_handling / ...)
  → Tools / MCP                (authorized tool calls via MCP servers)
  → PostgreSQL / Approved Knowledge
  → Worker response            (from approved knowledge / tool results, never fabricated)
  → FastAPI                    (persist message + action log, apply approval/escalation state)
  → Next.js                    (render response to customer)
```

## Approval / Escalation Flow

```text
Customer request
  → Worker detects ambiguous / unsupported / sensitive / high-risk, OR a tool
    failure, OR a state-changing action requiring approval
  → If escalation:  create escalations record with context; inform customer
    they are handed to a human; human agent resolves; outcome recorded.
  → If approval:    create approval_requests record (status=pending); Worker
    does NOT act; human agent approves or denies;
        Approved → Worker executes the gated action
        Denied   → Worker does not execute; informs customer appropriately
  → Traceable result: escalation/approval decision + worker_action_log entries
    recorded under the same trace_id (audit / replay).
```

## Deferred Decisions Resolved by This Plan

- **Initial knowledge-base scope** → seeded `knowledge_articles` starter set:
  return policy, password reset, shipping/order status, business hours, refund
  policy reference (Section 15).
- **Concrete tool-to-MCP mapping** → three MCP servers (knowledge, support-data,
  escalation-approval) mapping the six spec tools (Section 8).
- **Escalation/approval UX** → agent view in the frontend with
  open-escalation and pending-approval lists and Approve/Reject actions; customer
  sees a "handed to a human" / "requires review" notice (Section 3).
- **Data retention** → data minimization + defined retention (conversations,
  logs) enforced via policy and cleanup job; exact durations defined in tasks
  (Section 11 of spec deferred to planning).

## Assumptions

- Customers are authenticated by the host platform before any personal-data
  access (spec Assumptions).
- An admin-maintained approved knowledge base exists and is seeded for the MVP.
- Human agents and administrators are available to review escalations/approvals.
- Chat is the single channel; single default language; learning-scale load.
- PostgreSQL is the single source of truth; MCP servers are separate processes.

## Risks

- **LLM non-determinism** could cause classification drift → mitigated by
  deterministic rules + stable prompt + graders and containment measurement
  (NFR-005).
- **Over/under-escalation** affects containment and safety → mitigated by
  escalation precision grading (SC-004) and golden-set coverage.
- **Authorization bypass** would violate SC-005 → mitigated by enforcing session
  scoping and role limits in the tool/service layer (defense in depth), not only
  in prompts.
- **Scope creep** (extra channels, ticket updates) → explicitly out of scope
  (spec Section 19); tracked in Complexity Tracking.

## Tradeoffs

- **Standalone MCP servers vs in-process tools**: standalone servers add
  deployment complexity but give clear least-privilege boundaries and independent
  testing — chosen to demonstrate the Agent Factory tool surface faithfully.
- **Stateless Worker + persisted state vs in-memory session**: more DB I/O but
  reconstructable, testable, traceable behavior — chosen for evaluation and audit.
- **Monorepo vs separate repos**: monorepo is simpler to learn and run locally —
  chosen for this learning project.
- **Create+read-only tickets vs full CRUD**: less utility but safer and simpler —
  chosen per user decision and spec scope.

## Architectural Decisions

The following are architecturally significant (candidate ADRs — not auto-created):

- **AD-1**: Monorepo web-app structure (frontend + backend + worker + db).
- **AD-2**: AI Worker as a Python package using LLM tool-calling over MCP servers.
- **AD-3**: Hybrid authorization (customer session scoping + role-based worker
  permissions) enforced at the tool/service layer.
- **AD-4**: Create + read-only ticket operations enforced at the tool boundary.
- **AD-5**: MCP tool servers as separate processes for least privilege.
- **AD-6**: Evaluation-first with a golden set + graders + containment metric.

## Complexity Tracking

> The multi-component web structure is inherent to the feature (a chat UI calling
> an agent API), not accidental complexity.

| Violation (if any) | Why Needed | Simpler Alternative Rejected Because |
|--------------------|------------|--------------------------------------|
| Separate MCP server processes | Demonstrates the Agent Factory tool surface; enforces least-privilege boundaries | In-process tools rejected because they blur permission boundaries and are less faithful to the learning goal |
| 3-tier web app (frontend+backend+worker+db) | Feature requires a customer chat UI calling an agent API with persistence | A single-process CLI demo would not exercise the real request flow |
