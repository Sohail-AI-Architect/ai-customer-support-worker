---
id: 002
title: ADR Approval Gate Intent
stage: misc
date: 2026-08-10
surface: agent
model: oc/deepseek-v4-flash-free
feature: ai-support-worker
branch: 001-ai-support-worker
user: Sarah Sohail
command: /sp.adr approval-gate-intent
labels: ["adr", "architecture", "approval", "human-in-the-loop", "us5"]
links:
  spec: specs/001-ai-support-worker/spec.md
  ticket: null
  adr: history/adr/003-approval-gate-intent.md
  pr: null
files:
 - history/adr/003-approval-gate-intent.md (new ADR)
tests:
 - none (documentation)
---

## Prompt

/sp.adr approval-gate-intent — document the architecturally significant decision
cluster introduced by US5 implementation: the new `approval` intent and the
pending-approval lifecycle that is distinct from escalation. The ADR must cluster
related changes (classifier intent, approval_requests model + pending lifecycle,
approval.request MCP/API surface, agent approval queue, eval), list at least one
alternative with tradeoffs, cover positive and negative consequences, and link
back to the plan/spec. The user asked to document this decision following the
US5 implementation.

## Response snapshot

Created ADR-003 `approval-gate-intent.md` following the repo's existing ADR
structure (modeled on ADR-002). It documents the decision cluster:
- **Decision**: a separate `approval` intent (not folded into escalation), checked
  before high-risk words via a static `APPROVAL_ACTIONS` phrase→label map
  (cancel/delete/close/refund); propose-and-hold semantics with
  `approval_required=True`; pending lifecycle with audited approve/deny
  (`GET /api/agent/approvals`, `POST .../decision`, 409 if not pending); reuse of
  the session-scoped escalation-approval server and the ensure_customer_scope
  guard; deterministic trigger for evaluability (NFR-005).
- **Consequences**: positive — clear containment vs escalation, safety-by-
  construction (no execute-then-ask), pattern reuse, deterministic/testable,
  auditable. Negative — static trigger is coarse (paraphrase fall-through), two
  near-sibling flows to maintain, no customer-facing decision feedback yet,
  model-judged approval deferred.
- **Alternatives recalled**: reuse-escalation-only (rejected: conflates the two
  flows), auto-execute-then-audit (rejected: violates FR-014/015), model-judged
  ambiguity-blend (rejected for MVP: non-deterministic, contradicts NFR-005).
- **References**: plan Section 14 (approval vs escalation) and FR-014/015;
  related to ADR-001 and ADR-002.

## Outcome

- ✅ Impact: Records the safety-relevant decision separating "hand off" from
  "propose and wait" — a core, cross-cutting model decision (FR-014/015, SC-006,
  NFR-005). Passed the three-part significance test (impact / alternatives /
  scope) and the flywheel checklist grader (clustered, has alternatives, pros/
  cons, concise).
- 🧪 Tests: none — documentation only (represents implemented, green behavior:
  backend 61, mcp 8, golden eval 14/14 recorded in the ADR's evaluation evidence).
- 📁 Files: created history/adr/003-approval-gate-intent.md.
- 🔁 Next prompts: review ADR with team; proceed to Phase8 Polish (T058-T063).
- 🧠 Reflection: The ADR deliberately scopes the trigger to a deterministic
  keyword map rather than model judgment, and documents that a model-judged
  sensitive-action detector would be a future enhancement — keeping the MVP
  evaluable while noting the upgrade path.

## Evaluation notes (flywheel)

- Failure modes observed: none — no create-adr.sh script exists in this repo, so
  the ADR was written directly following the format of 002-ticket-operations-model.md.
- Graders run and results (PASS/FAIL): flywheel checklist — clustered (PASS),
  alternatives (PASS), pros/cons (PASS), concise (PASS).
- Prompt variant (if applicable): n/a — documentation command.
- Next experiment (smallest change to try): none for ADR authoring; implementation
  evidence is already green.