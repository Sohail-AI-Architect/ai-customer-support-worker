# MCP Tool Contract: AI Customer Support Worker

**Phase 1 output** — concrete tool-to-MCP mapping (plan Section 8, research R2)
and each tool's contract. Tools are the Worker's only way to act; each has
boundaries, permissions, inputs, outputs, and failure handling (constitution
Principle 5).

## Tool-to-MCP mapping

| MCP server | Tool | Permission | Side effects |
|------------|------|-----------|--------------|
| `knowledge-server` | `knowledge.search` | read-only, always allowed | none |
| `support-data-server` | `customer.info.get` | read-only, scoped to session customer | none |
| `support-data-server` | `ticket.get` | read-only, scoped to session customer | none |
| `support-data-server` | `ticket.list` | read-only, scoped to session customer | none |
| `support-data-server` | `ticket.create` | write, create only | inserts a ticket |
| `escalation-approval-server` | `escalation.create` | write, worker-initiated | inserts an escalation |
| `escalation-approval-server` | `approval.request` | write, worker-initiated | inserts an approval request |

## Tool contracts

### knowledge.search
- Input: `{ query: string, limit?: int }`
- Output: `{ articles: [ { id, question, answer, keywords } ] }` (approved only)
- Permission: always allowed (approved knowledge is public to the Worker).
- Failure: `{ error: "knowledge_unavailable" }` → Worker fails safely.

### customer.info.get
- Input: `{ customer_id: string }`
- Output: `{ id, name, status }`
- Permission: only if `customer_id == session.customer_id`.
- Failure: `{ error: "unauthorized" }` or `{ error: "customer_not_found" }`.

### ticket.get
- Input: `{ ticket_id: string }`
- Output: ticket object.
- Permission: only if the ticket belongs to `session.customer_id`.
- Failure: `{ error: "unauthorized" }` or `{ error: "ticket_not_found" }`.

### ticket.list
- Input: `{}`
- Output: `{ tickets: [ ... ] }` for `session.customer_id`.
- Failure: `{ error: "tickets_unavailable" }`.

### ticket.create
- Input: `{ subject: string, description: string }`
- Output: `{ id, subject, status: "open" }`
- Permission: write allowed; **create only**. No update/close/delete capability
  is exposed by this server.
- Failure: `{ error: "ticket_create_failed" }`.

### escalation.create
- Input: `{ conversation_id, reason, context }`
- Output: `{ id, status: "open" }`
- Failure: `{ error: "escalation_failed" }`.

### approval.request
- Input: `{ conversation_id, proposed_action, payload }`
- Output: `{ id, status: "pending" }`
- Failure: `{ error: "approval_request_failed" }`.

## Failure handling rules

- Tools never raise outside their server; they return structured error objects.
- On any tool error, the Worker does **not** guess — it escalates or states it
  cannot complete the request (spec FR-005, plan Section 17).
- Every tool call is logged to `worker_action_log` with `trace_id` and an input
  hash (no raw personal data).
