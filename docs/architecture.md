# Architecture: AI Customer Support Worker

> Architecture notes for the AI Customer Support Digital FTE. This is the
> runnable summary of `specs/001-ai-support-worker/plan.md` (Sections 1–2, 5–14).
> Authoritative details live in the plan, `data-model.md`, and `contracts/`.

## 1. System overview

A **3-tier web application** with an integrated AI agent:

- **Frontend** (Next.js): customer chat UI (`/chat`) + human-agent surfaces
  (`/agent`, and future approvals). Calls the backend over HTTP(S).
- **Backend API** (FastAPI): owns authentication/authorization, the chat
  endpoint, ticket endpoints, knowledge lookup, and agent-facing
  escalation/approval endpoints. Owns all business rules and persistence.
- **AI Worker** (Python, `backend/src/worker`): the Digital FTE. Receives a
  chat message, classifies intent, selects a skill, invokes tools, builds a
  response, and decides when to escalate or request approval.
- **PostgreSQL**: single source of truth (customers, conversations, messages,
  tickets, knowledge, escalations, approvals, action log).
- **MCP tool servers** (`mcp-servers/`): bounded, permissioned tool surfaces the
  Worker uses to act on knowledge, customer data, tickets, and escalations.

The Worker **never talks to PostgreSQL directly**; it acts through MCP-exposed
tools, which are thin, authorized service calls. This enforces least privilege
and a single contract surface.

## 2. Repository layout

```text
frontend/           Next.js app (customer + agent surfaces)
backend/            FastAPI API + AI Worker + domain + persistence
  src/
    api/            REST routers + deps (customer/agent auth)
    domain/         authorization (session scope, roles)
    models/         SQLAlchemy ORM models
    services/       business services (knowledge, tickets, escalations, ...)
    worker/         WorkerAgent + skills
mcp-servers/        standalone MCP tool servers (knowledge, support-data,
                    escalation-approval)
eval/               golden set + graders + evaluation runner
migrations/         Alembic DB migrations (repo root)
docs/               this documentation + runbook
specs/001-ai-support-worker/   spec, plan, tasks, data-model, contracts, quickstart
```

## 3. Request flow

1. A customer posts a message to `POST /api/chat` with `X-Customer-Id`.
2. The API resolves/creates the customer, loads/creates the conversation, and
   persists the customer message.
3. The **WorkerAgent** is invoked with the message and a `trace_id`:
   - **Classify** intent → `answer` | `retrieve` | `create_ticket` |
     `escalate` | `out_of_scope`.
   - **Select a skill** and invoke the relevant **tool**.
   - **Build a response** and decide resolve / escalate / request-approval.
4. The reply, conversation, worker action log, and any escalation are persisted.
5. An `X-Trace-Id` propagates so the request can be replayed/audited end to end.

## 4. AI Worker responsibilities

The Worker is **stateless** per call; conversation history is loaded from
persisted state by the API layer. It is **deterministic where possible**
(NFR-005): no LLM call in the match/classify path.

### Intent classification

| Intent | Trigger | Action |
|--------|---------|--------|
| `answer` | Approved-knowledge question | Look up knowledge, never fabricate |
| `retrieve` | "my order/tickets" (not a how-to) | Read the customer's own data |
| `create_ticket` | "create/open/file a ticket" | Create a ticket (create-only) |
| `escalate` | high-risk, sensitive, unsupported, or modify-existing-ticket | Hand to a human with context |
| `out_of_scope` | clearly outside scope | Refuse and escalate |

### Skills (reusable domain actions)

| Skill | Responsibilities |
|-------|------------------|
| `approved_knowledge_lookup` | Match question → approved article; no match → refuse |
| `customer_context` | Read the session customer's own profile/tickets |
| `ticket_handling` | Create a ticket (create + read only) |
| `escalation_triage` | Record an escalation with context (worker-initiated, audited) |

### Tools / MCP servers

| MCP server | Tools | Scope |
|------------|-------|-------|
| `knowledge-server` | `knowledge.search` | read-only, always allowed |
| `support-data-server` | `customer.info.get`, `ticket.get`, `ticket.list`, `ticket.create` | session-scoped; create + read only |
| `escalation-approval-server` | `escalation.create` (+ `approval.request` for US5) | worker-initiated, audited, session-scoped |

## 5. Security model

- **Hybrid authorization** (plan Section 12): every data action requires both
  session scoping (the request belongs to the authenticated customer) **and** a
  Worker role check.
- **Session scoping** is enforced at the service/tool layer, so the Worker
  cannot address another customer's data (FR-006, SC-005).
- **Create + read only** for tickets (FR-010): there is no update/close/delete
  surface. Requests to modify an existing ticket escalate (FR-011). See
  `history/adr/002-ticket-operations-model.md`.
- **Never fabricate** (FR-003/004/005): no approved answer → refuse/escalate.
  See `history/adr/001-knowledge-matching-strategy.md`.
- **Human-in-the-loop** (US4/US5): escalations and approvals are persisted,
  audited, and resolved by a human agent.

## 6. Related artifacts

- Plan: `specs/001-ai-support-worker/plan.md`
- Data model: `specs/001-ai-support-worker/data-model.md`
- API contract: `specs/001-ai-support-worker/contracts/openapi.yaml`
- Tool/MCP contract: `specs/001-ai-support-worker/contracts/mcp-tools.md`
- ADRs: `history/adr/001-knowledge-matching-strategy.md`,
  `history/adr/002-ticket-operations-model.md`
- Runbook: `docs/runbook.md`
