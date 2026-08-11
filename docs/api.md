# API Usage

> Human-readable usage guide for the REST API. The machine-readable contract is
> `specs/001-ai-support-worker/contracts/openapi.yaml`. Base URL in local dev:
> `http://localhost:8000`. Interactive docs: `http://localhost:8000/docs`.

## Authentication

Two headers identify the caller (MVP session stand-in; hardened in a later
story):

| Header | Used for | Notes |
|--------|----------|-------|
| `X-Customer-Id` | customer endpoints | resolves/creates the customer; all data access is scoped to this id |
| `X-User-Id` | agent endpoints | a user id (UUID) or username; agent/admin role required |

## Customer endpoints

### `POST /api/chat` — send a message to the Worker

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" -H "X-Customer-Id: demo-customer-1" \
  -d '{"message": "What is your return policy?"}'
```

Response:

```json
{
  "conversation_id": "...",
  "reply": "Our return policy is...",
  "intent": "answer",
  "escalated": false,
  "approval_required": false,
  "trace_id": "..."
}
```

`intent` is one of `answer` | `retrieve` | `create_ticket` | `escalate` |
`out_of_scope`. When `escalated` is true, an open escalation is persisted for
the conversation.

### `GET /api/tickets` — list the customer's own tickets

```bash
curl http://localhost:8000/api/tickets -H "X-Customer-Id: demo-customer-1"
```

Returns a JSON array of the authenticated customer's tickets only.

### `POST /api/tickets` — create a ticket

```bash
curl -X POST http://localhost:8000/api/tickets \
  -H "Content-Type: application/json" -H "X-Customer-Id: demo-customer-1" \
  -d '{"subject": "Broken checkout", "description": "Cannot complete purchase."}'
```

Returns `201` with the created ticket (`status: "open"`).

### `GET /api/tickets/{id}` — get one ticket

Returns the ticket if it belongs to the caller; refused (403/404) otherwise.

> Tickets are **create + read only**. There is **no** `PUT/PATCH/DELETE
> /api/tickets/{id}` (FR-010).

## Agent endpoints (agent/admin role required)

### `GET /api/agent/escalations` — list open escalations

```bash
curl http://localhost:8000/api/agent/escalations -H "X-User-Id: demo-agent-1"
```

Returns open escalations, newest first, with `reason`, `context`, `status`.

### `POST /api/agent/escalations/{id}/resolve` — mark resolved

```bash
curl -X POST http://localhost:8000/api/agent/escalations/<escalation-id> \
  -H "X-User-Id: demo-agent-1"
```

Sets the escalation to `resolved` and records the acting agent.

## Health

### `GET /health`

```bash
curl http://localhost:8000/health
# {"status": "ok", "app": "AI Customer Support Worker"}
```
