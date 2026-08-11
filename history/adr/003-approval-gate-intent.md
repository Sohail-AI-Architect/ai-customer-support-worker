# ADR-003: Approval-Gate Intent & Pending Approval Lifecycle

> **Scope**: Document the decision cluster governing how the Worker handles
> sensitive/irreversible actions that it may *propose* but must not execute
> without a human decision. Covers the new `approval` intent in classification,
> the pending-approval lifecycle (propose → approve/deny → audit) that is
> distinct from escalation, and the session-scoped worker-initiated tool that
> persists it.

- **Status:** Accepted
- **Date:** 2026-08-10
- **Feature:** 001-ai-support-worker
- **Context:** US5 (P4) is the second worker-initiated, human-in-the-loop flow.
  The spec draws a deliberate distinction between two failure-handling paths
  (plan Section 14): **escalation** — ambiguous/unsupported/high-risk requests are
  handed to a human to resolve; and **approval** — an action that is *sensitive or
  irreversible* (cancel, delete, close, refund) is proposed and held pending a
  human decision (spec FR-014, FR-015; constitution Principle 6 Human-in-the-Loop;
  SC-006). The central question is how the Worker should signal and persist "this
  needs a human decision before I act," given the requirement that it must NOT
  execute sensitive actions and MUST record the decision for audit. This decision
  is cross-cutting: it introduces a new intent to the trend classification,
  a new `approval_requests` data object and pending lifecycle, a new MCP/API
  surface that reuses the escalation-approval server, and a new agent-facing
  approval queue.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/safety? Yes — how the
        Worker distinguishes "hand off" (escalation) from "propose and wait"
        (approval) is a core safety model decision (FR-014/015, SC-006, NFR-005),
        and it shapes classification, data, tool contract, and UI in lockstep.
     2) Alternatives: Multiple viable options considered with tradeoffs? Yes —
        reuse-escalation-only, auto-execute-then-audit, ambiguity-blend, and the
        chosen separate-intent approach.
     3) Scope: Cross-cutting concern? Yes — classifier, `approval_requests` model,
        MCP server, REST API, agent UI, and eval all change together. -->

## Decision

- **Separate `approval` intent (not folded into escalation):** the classifier
  gains `Intent.APPROVE`, triggered before the high-risk/escalate words by a
  bounded `APPROVAL_ACTIONS` list of *state-changing* phrases (cancel/delete/
  close/refund). So "cancel my account" gates approval, while informational
  complaints ("I want to request a refund", "sue") still escalate. The two flows
  stay distinct so a denial can be honored without burying the request in the
  escalation queue (FR-014/015).
- **Propose, never execute:** on an `approval` intent the Worker replies that it
  needs human approval, sets `approval_required=True`, and does **not** perform
  the action. The chat API persists a pending `approval_requests` row via a
  session-scoped, worker-initiated `approval.request` tool (reusing the
  escalation-approval MCP server; FR-014).
- **Pending lifecycle with audited decision:** an approval starts `pending`; a
  human agent lists pendings (`GET /api/agent/approvals`) and approves/denies
  (`POST /api/agent/approvals/{id}/decision`, returning **409** if it is no
  longer pending). The decision (`decided_by`, `decided_at`) is recorded for
  audit; a denial is honored (the Worker already did not act) (FR-015).
- **Session-scoped like escalation:** `approval.request` refuses cross-customer
  conversations via the same `SessionScope` + `ensure_customer_scope` guard as
  escalation, maintaining the containment invariant (FR-006, SC-005).
- **Minimal, deterministic trigger:** `APPROVAL_ACTIONS` is a static
  phrase→label map (e.g. `cancel_subscription`, `delete_account`), keeping the
  gate predictable and evaluable (NFR-005) rather than model-judged.

## Consequences

### Positive

- **Clearest failure containment:** escalation and approval occupy distinct
  queues and intents, so an action awaiting a human decision is not confused with
  a case handed to a human to resolve. Denials are honored because the Worker
  never acted in the first place.
- **Safety-by-construction:** the Worker physically cannot perform a sensitive
  state-change it proposes; the only write is the audit/proposal record. There is
  no "execute then ask" path (FR-014).
- **Reuse of a proven pattern:** the approval tool rides the existing
  escalation-approval MCP server and session-scoping helpers, so the security and
  audit guarantees are consistent with escalation and ticket creation.
- **Deterministic and testable:** the phrase→action map is unit-tested, and the
  lifecycle is covered end to end (integration + contract + golden eval US5-001/002).
- **Auditable:** every decision is recorded (`decided_by`/`decided_at`), and
  every tool call is logged to `worker_action_log` with a `trace_id`.

### Negative

- **Static trigger is coarse:** `APPROVAL_ACTIONS` matches literal phrases, so
  paraphrases ("get rid of my account") may fall through to escalate or answer
  rather than approval. This is acceptable for the MVP and is bounded/deterministic.
- **Two near-sibling flows to maintain:** escalation and approval share vocabulary
  but differ in lifecycle; engineers must keep their data objects and endpoints
  distinct to preserve the separation this decision relies on.
- **No customer-facing decision feedback yet:** the Worker holds pending but does
  not re-notify the customer on decision in this story; a later story could push
  the outcome back into the conversation.
- **Model-judged approval is deferred:** the trigger is keyword-based, not an LLM
  safety classification; richer sensitive-action detection would be a follow-up
  (and itself would warrant review).

## Alternatives Considered

- **Alternative A — Reuse escalation only (no separate intent):** treat every
  sensitive action as an escalation with a "needs approval" flavor. **Rejected:**
  conflates "hand this to a human to do" with "hold this, wait for my decision."
  A denial would not carry a clean lifecycle, and the customer-facing wording and
  the agent workflow would blur FR-014 with FR-013.
- **Alternative B — Auto-execute then audit:** let the Worker perform sensitive
  actions and simply log them for later review. **Rejected:** directly violates
  FR-014/FR-015 and the constitution's Human-in-the-Loop and AI-safety principles;
  irreversible actions must never be taken before a human decision.
- **Alternative C — Ambiguity-blend (escalate-or-approve by model judgment):**
  leave the sensitive/approve classification to the LLM. **Rejected for MVP:**
  non-deterministic and hard to evaluate; contradicts deterministic-where-possible
  (NFR-005). The static `APPROVAL_ACTIONS` map favors predictability; a model-judged
  variant can be layered later behind the same lifecycle.

## References

- Feature Spec: `specs/001-ai-support-worker/spec.md` (FR-012, FR-013, FR-014,
  FR-015; SC-006; US5 acceptance scenarios; Section 12 Human Approval)
- Implementation Plan: `specs/001-ai-support-worker/plan.md` (Section 6 skill
  selection; Section 8 MCP tool mapping — approval.request; Section 12
  authorization; Section 14 Human Approval and Escalation Architecture)
- Related ADRs: ADR-002 (ticket create+read-only) noted that a future approval
  flow (US5) would be the gate for any richer ticket operations; ADR-001 governs
  the separate approved-knowledge path.
- Evaluator Evidence: `history/prompts/001-ai-support-worker/001-us5-human-approval.green.prompt.md`
  (backend 61 passed; mcp 8 passed; golden eval 14/14, US5-001/002 approval cases
  green; ruff clean).