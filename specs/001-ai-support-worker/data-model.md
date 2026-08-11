# Data Model: AI Customer Support Worker

**Phase 1 output** — PostgreSQL schema derived from the approved spec (Section 11)
and plan (Section 9). Defines entities, fields, relationships, validation, and
state transitions. Storage/ORM details are implementation concerns covered in
tasks; this is the domain model.

## Entities

### customers
Represents a customer who requests support.

| Field | Type | Notes |
|-------|------|-------|
| id | PK (uuid) | |
| external_id | text, unique | identity from the host/auth platform |
| name | text | display name |
| status | text | `active` \| `suspended` |
| created_at | timestamptz | |

Validation: `status` in (`active`, `suspended`); `external_id` unique, non-empty.

### users
Internal users: human agents and administrators (for auth roles).

| Field | Type | Notes |
|-------|------|-------|
| id | PK (uuid) | |
| username | text, unique | |
| role | text | `agent` \| `admin` |
| created_at | timestamptz | |

Validation: `role` in (`agent`, `admin`).

### support_tickets
Support tickets the Worker may **read** and **create** (never update/close/delete).

| Field | Type | Notes |
|-------|------|-------|
| id | PK (uuid) | |
| customer_id | FK → customers | session-scoped |
| subject | text | |
| description | text | |
| status | text | `open` \| `in_progress` \| `resolved` \| `closed` |
| created_at | timestamptz | |

Validation: `status` default `open`; `subject` non-empty.

### conversations
A chat session between a customer and the Worker.

| Field | Type | Notes |
|-------|------|-------|
| id | PK (uuid) | |
| customer_id | FK → customers | |
| channel | text | `chat` (single channel in scope) |
| status | text | `open` \| `escalated` \| `closed` |
| started_at | timestamptz | |
| updated_at | timestamptz | |

Validation: `channel` = `chat`; `status` in (`open`, `escalated`, `closed`).

### conversation_messages
Messages in a conversation (customer, worker, or system).

| Field | Type | Notes |
|-------|------|-------|
| id | PK (uuid) | |
| conversation_id | FK → conversations | |
| role | text | `customer` \| `worker` \| `system` |
| content | text | |
| trace_id | text | links to worker action log |
| created_at | timestamptz | |

Validation: `role` in (`customer`, `worker`, `system`).

### knowledge_articles
Approved knowledge — the only source of truth the Worker answers from.

| Field | Type | Notes |
|-------|------|-------|
| id | PK (uuid) | |
| question | text | canonical question |
| answer | text | approved answer |
| keywords | text[] | retrieval matching |
| status | text | `approved` \| `draft` \| `archived` |
| updated_at | timestamptz | |

Validation: `status` default `approved`; Worker answers only from `approved` rows.

### escalations
Records of cases handed to a human agent.

| Field | Type | Notes |
|-------|------|-------|
| id | PK (uuid) | |
| conversation_id | FK → conversations | |
| reason | text | classification reason (e.g., sensitive, high-risk, unsupported) |
| context | text | conversation summary + relevant authorized data |
| status | text | `open` \| `assigned` \| `resolved` |
| handled_by | FK → users (nullable) | |
| created_at | timestamptz | |
| resolved_at | timestamptz | nullable |

Validation: `status` in (`open`, `assigned`, `resolved`).

### approval_requests
Sensitive/state-changing actions proposed by the Worker, awaiting human decision.

| Field | Type | Notes |
|-------|------|-------|
| id | PK (uuid) | |
| conversation_id | FK → conversations | |
| proposed_action | text | description of the gated action |
| payload | jsonb | parameters of the action if approved |
| status | text | `pending` \| `approved` \| `denied` |
| decided_by | FK → users (nullable) | |
| decided_at | timestamptz | nullable |
| created_at | timestamptz | |

Validation: `status` in (`pending`, `approved`, `denied`).

### worker_action_log
Observability/audit: every Worker action, tool call, decision, and data access.

| Field | Type | Notes |
|-------|------|-------|
| id | PK (uuid) | |
| trace_id | text, indexed | end-to-end trace |
| conversation_id | FK → conversations | |
| action | text | e.g., `answer`, `ticket.create`, `escalate`, `approval.request` |
| tool | text | tool invoked, if any |
| input_hash | text | hashed tool input (avoids storing raw personal data) |
| outcome | text | `ok` \| `denied` \| `error` \| `escalated` |
| created_at | timestamptz | |

Validation: `outcome` in (`ok`, `denied`, `error`, `escalated`).

## Relationships

- `customers` 1–N `support_tickets`
- `customers` 1–N `conversations`
- `conversations` 1–N `conversation_messages`
- `conversations` 0–1 `escalations`
- `conversations` 0–N `approval_requests`
- `conversations` 1–N `worker_action_log`
- `users` 0–N `escalations.handled_by`
- `users` 0–N `approval_requests.decided_by`

## State Transitions

- **conversation.status**: `open` → `escalated` → `closed`; `open` → `closed`.
- **escalation.status**: `open` → `assigned` → `resolved`.
- **approval_requests.status**: `pending` → `approved` | `denied` (terminal).
- **support_tickets.status**: managed only by humans; Worker may set to `open` on
  creation and never transitions it.

## Authorization Mappings

- **customer.info.get** → reads `customers` row where `id = session.customer_id`.
- **ticket.get/list** → rows where `customer_id = session.customer_id`.
- **ticket.create** → creates a row with `customer_id = session.customer_id`.
- **escalation.create / approval.request** → insert rows linked to the current
  conversation; worker-initiated; audited.
- **No update/close/delete** endpoints or tool capabilities exist for tickets
  (spec FR-010).
