# ADR-002: Ticket Operations Model (Create + Read Only)

> **Scope**: Document the decision cluster governing how the Worker may act on
> support tickets. Covers the create-only write surface, the hard prohibition
> on update/close/delete, the escalate-on-modify behavior, and the session
> scoping that binds every ticket action to the authenticated customer.

- **Status:** Accepted
- **Date:** 2026-08-09
- **Feature:** 001-ai-support-worker
- **Context:** US3 (P3) gives the Worker its first authorized **write** action —
  creating a support ticket when a customer reports an issue. The constitution
  and spec require bounded, least-privilege, low-risk action (constitution
  Principle 5; FR-009/FR-010/FR-011). A customer may also have read access to
  their own tickets (US2), and requests to modify an existing ticket must never
  be honored by the Worker (FR-011). The central question is what write model
  the Worker should operate under: whether it may freely mutate tickets, or
  whether its surface is deliberately narrowed to a safe subset. This decision
  is cross-cutting — it defines the ticket data model, the REST and MCP tool
  contracts, and the Worker's classification behavior, and it must be consistent
  across every current and future user story.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? Yes —
        the ticket write model is a data-model + authorization decision with
        security implications (FR-010/FR-011, SC-005), and it shapes the API and
        MCP tool surface for all ticket stories.
     2) Alternatives: Multiple viable options considered with tradeoffs? Yes —
        full CRUD, worker-mediated status updates, workflow/state-machine based
        changes.
     3) Scope: Cross-cutting concern (not an isolated detail)? Yes — it touches
        the data model, REST endpoints, MCP tools, the Worker agent, and
        authorization in lockstep. -->

## Decision

- **Create-only write surface:** the Worker may **create** a ticket
  (`ticket.create` / `POST /api/tickets`), never update, close, or delete. The
  REST router and the support-data MCP tool expose **no** update/close/delete
  capability — the absence is structural, not just prompt-enforced (FR-010).
- **Escalate-on-modify:** when a customer asks to change, close, or delete an
  existing ticket, the Worker does not act; it escalates to a human
  (classification returns `escalate` with reason `ticket_modify`) (FR-011).
- **Session scoping:** every ticket read and create is bound to the
  authenticated customer's id at the service/tool layer (`SessionScope` +
  `ensure_customer_scope`). Cross-customer reads/creates are refused (FR-006,
  SC-005) — it is structurally impossible for the Worker to address another
  customer's ticket.
- **Status is a fixed, defaulted value:** new tickets are created with
  `status = "open"`. Status changes are a human/agent responsibility, not a
  Worker action, in this MVP.
- **Two enforcement layers:** role-based Worker permissions (create+read only)
  are enforced in the MCP tool layer, and session scoping is enforced in the
  API/service layer — both checks must pass for any ticket action (hybrid
  authorization, plan Section 12).

## Consequences

### Positive

- **Bounded blast radius:** the Worker's first write action is low-risk,
  append-only, and cannot corrupt or destroy existing data.
- **Security-by-construction:** because update/close/delete do not exist, they
  cannot be mis-invoked, prompt-injected, or abused by a compromised model call.
- **Consistent enforcement:** the same create+read-only rule is applied at both
  the REST boundary and the MCP tool boundary, and escalate-on-modify is wired
  into intent classification — no single layer can silently bypass it.
- **Cross-customer protection:** session scoping at the data layer guarantees a
  customer cannot see or write another customer's tickets, satisfying the
  containment success metric (SC-005).
- **Simple, auditable:** the ticket surface is easy to reason about, test, and
  extend; every ticket action is audited via `worker_action_log`.

### Negative

- **Inflexibility for common flows:** the Worker cannot resolve/close its own
  tickets, so resolution remains human-mediated. A customer asking for a status
  change always gets escalation, which may feel heavy for benign requests.
- **No partial autonomy:** richer ticket workflows (e.g., "mark as resolved")
  are deferred; they would require an explicit, gated decision (likely an
  approval flow, US5) before being added.
- **Create surface still needs guards:** creation uses the message text as
  subject/description — bounded and non-fabricated, but not curated; a future
  refinement could structure subject vs. description extraction.

## Alternatives Considered

- **Alternative A — Full CRUD (create, read, update, close, delete):** gives the
  Worker maximum autonomy. **Rejected for MVP:** highest blast radius and the
  most risk to a learning/AI worker; violates least-privilege and the
  create+read-only constraint the spec explicitly demands (FR-010). Could be
  revisited per-operation behind approval gates.
- **Alternative B — Worker-mediated status updates with a workflow/state
  machine:** allow the Worker to advance tickets along an allowed status path
  (e.g., open → in_progress) under rules. **Rejected for MVP:** introduces a
  state machine, more validation surface, and more ways to act incorrectly,
  without a story that needs it yet. Kept as a candidate for future stories.
- **Alternative C — Prompt-only restriction (no structural enforcement):** tell
  the Worker via prompt not to modify tickets, but still expose update/close/
  delete endpoints and tools. **Rejected:** relies entirely on model compliance;
  the endpoints remain callable and are a fabrication/safety hazard. Structural
  absence is strictly safer and aligns with deterministic-where-possible
  (NFR-005).

## References

- Feature Spec: `specs/001-ai-support-worker/spec.md` (FR-006, FR-009, FR-010,
  FR-011; SC-005; US3 acceptance scenarios)
- Implementation Plan: `specs/001-ai-support-worker/plan.md` (Section 8 MCP
  tool mapping; Section 12 hybrid authorization; Section 13 Ticket Operations)
- Related ADRs: ADR-001 (approved-knowledge matching) governs the separate
  question-answering path; this ADR governs the ticket action path.
- Evaluator Evidence: `history/prompts/001-ai-support-worker/006-implement-us3-ticket-creation.implement.prompt.md`
  (US3 golden eval 2/2; integration asserts PATCH/PUT/DELETE → 405 and
  cross-customer GET refused with 403/404).
