<!--
  ============================================================================
  SYNC IMPACT REPORT (v0.0.0 → v1.0.0)
  ----------------------------------------------------------------------------
  Version change: 0.0.0 (unratified template) → 1.0.0 (initial ratification)

  Modified principles (old title → new title):
    - (none; template was unratified — all principle placeholders are new)

  Added sections:
    - 14 numbered Core Principles (Spec-Driven Development through
      Separation of Concerns)
    - "Lifecycle & Non-Negotiables" (SECTION_2)
    - "Technology Context" (SECTION_3)
    - Governance (amendment procedure, versioning policy, compliance review)

  Removed sections:
    - (none)

  Templates requiring updates:
    ✅ .specify/templates/plan-template.md  — Constitution Check gate aligns
    ✅ .specify/templates/spec-template.md  — outcome/acceptance alignment
    ✅ .specify/templates/tasks-template.md — testing/observability discipline
    ✅ .claude/commands/sp.constitution.md  — no outdated references

  Follow-up TODOs:
    - (none — all placeholders resolved at ratification)
  ============================================================================
-->

# AI FDE Lab Constitution

> This constitution governs all future development in the AI FDE Lab. It is a
> practical learning project for building a production-oriented **Digital FTE /
> AI Worker** through **Spec-Driven Development (SDD)**. Every artifact and
> decision in this repository MUST be traceable to an Outcome and consistent
> with the principles below.

## Core Principles

### 1. Spec-Driven Development (SDD)

Specification, planning, implementation, and evaluation are separate, ordered
phases. The project lifecycle MUST follow:

**Outcome → Constitution → Specification → Plan → Tasks → Implementation →
Evaluation → Verification → Deployment**

- Specifications MUST define **WHAT** and **WHY** before any implementation.
- Plans MUST define **HOW** without prematurely implementing features.
- Tasks MUST be derived from the approved Specification and Plan.
- Implementation MUST follow the approved Specification, Plan, and Tasks.
- No phase MAY skip or reorder a preceding required phase.
- Each phase produces a durable artifact (spec.md, plan.md, tasks.md) that is
  reviewed before the next phase begins.

**Why**: A Digital FTE / AI Worker is only trustworthy if its behavior is
derived from an agreed outcome rather than ad-hoc reasoning. SDD makes intent
auditable and reversible.

### 2. Outcome-First Engineering

Every feature MUST begin with a clear, measurable business outcome and explicit
acceptance criteria before design or code.

- Features MUST NOT be started without a defined Outcome and Acceptance
  Criteria.
- Acceptance criteria MUST be specific, measurable, and testable.
- Work is judged complete only when the Outcome is demonstrably achieved, not
  when the code compiles.
- Non-goals MUST be recorded to prevent scope creep.

**Why**: Learning is only validated if each increment provably delivers value;
outcome-first prevents "solutionism" and busywork.

### 3. Digital FTE / AI Worker Architecture

The product is a Digital Full-Time-Equivalent (Digital FTE / AI Worker) that
performs work autonomously under defined boundaries.

- AI Worker behavior MUST be **deterministic where possible** and evaluated
  with measurable criteria.
- The Worker's capabilities, boundaries, and failure modes MUST be explicit.
- The Worker MUST be able to request escalation or pause when it cannot meet a
  defined contract.
- Architecture MUST be simple enough to learn from while meeting
  production-quality engineering practices.

**Why**: Deterministic, bounded behavior is a precondition for trust,
testing, and evaluation of an autonomous worker.

### 4. Reusable Skills and Domain Knowledge

Domain knowledge and operational procedures MUST be packaged as reusable
**Skills**.

- Skills MUST contain reusable domain knowledge and operational instructions,
  not one-off code.
- Skills MUST be discoverable, versioned, and tested.
- A Skill MUST declare its inputs, outputs, and when it applies.
- Do NOT duplicate knowledge across Skills; extract and share it.

**Why**: Skills are the unit of institutional memory — they let the AI Worker
reliably repeat what it learned once.

### 5. Tools and MCP Integrations

Tools and MCP (Model Context Protocol) servers are the Worker's only way to
act on the world.

- Every Tool MUST have clear boundaries, permissions, inputs, outputs, and
  failure handling.
- Tool contracts MUST be documented and versioned.
- Tools MUST fail safely and report failures explicitly to the Worker.
- MCP integrations MUST be configured with the least privilege required.
- Do NOT grant a Tool capabilities it does not need.

**Why**: A well-bounded tool surface is what makes an AI Worker safe and
predictable. Ambiguous tools produce ambiguous actions.

### 6. Evaluation-First Development

Evaluation is not a final step — it is designed first and applied continuously.

- Evaluation criteria MUST be defined alongside the Outcome and Acceptance
  Criteria.
- The Worker's outputs MUST be evaluated against measurable criteria
  (graders, golden tests, and metrics).
- Red-Green-Refactor discipline: tests/evals MUST be written and shown to fail
  before implementation.
- Evaluation results MUST be recorded for every implemented change.

**Why**: You cannot improve a Worker you cannot measure. Evaluation-first
turns quality into a verifiable property.

### 7. Human-in-the-Loop Workflows

The Worker MUST operate with human oversight where risk or judgment is
involved.

- Sensitive operations MUST support human approval or escalation.
- High-risk actions MUST require human confirmation before execution.
- The Worker MUST surface uncertainty and stop when it is out of scope.
- Escalation paths MUST be defined before the Worker is deployed.

**Why**: Autonomy must be bounded by consent. The human stays accountable for
outcomes the Worker is not authorized to decide alone.

### 8. AI Safety and Governance

The Worker and its development process MUST respect safety and governance
principles.

- Behaviors that cause irreversible or high-impact harm MUST be gated by
  approval.
- The Worker MUST NOT take actions without a defined authorization boundary.
- Governance decisions (data handling, autonomy limits, model choice) MUST be
  documented.
- Use the strongest capable AI model only where justified; otherwise use the
  smallest sufficient model.

**Why**: Governance keeps autonomy aligned with user intent and prevents
misuse, drift, and accountability gaps.

### 9. Security and Least-Privilege Access

Security is a design constraint, not an afterthought.

- External actions MUST follow least-privilege principles.
- Secrets MUST NEVER be hardcoded or committed to Git; use `.env` and vault
  tooling.
- Credentials MUST be scoped to the minimum permission required for the task.
- No unauthenticated or over-privileged defaults.
- Security-sensitive changes MUST be reviewed before merge.

**Why**: The most common AI-Worker failure is accidental escalation of
privilege; least-privilege contains blast radius.

### 10. Testing and Verification

All changes MUST be testable and verifiable.

- Each change MUST include tests or a verification path that demonstrates it
  works.
- Tests MUST be reproducible and run in CI.
- Verification MUST confirm both functional correctness and acceptance
  criteria.
- A change that cannot be tested is not done.

**Why**: Unverifiable changes erode trust in the Worker and the codebase.

### 11. Observability and Traceability

Every action MUST be observable and traceable back to its origin.

- Traceability MUST be preserved from business Outcome → Specification →
  Implementation → Evaluation.
- The Worker MUST emit structured, actionable logs for its actions and
  decisions.
- Each Prompt History Record (PHR) MUST record the originating prompt verbatim.
- Metrics and logs MUST support replay and audit of Worker behavior.

**Why**: You can only audit, debug, and improve a Worker whose behavior you can
observe and trace.

### 12. Production Readiness

Learning does not excuse fragility. Deliverables MUST be runnable and robust.

- Deliverables MUST meet production-quality engineering standards (error
  handling, resource limits, failure recovery).
- Dependency versions MUST be pinned and reproducible.
- Deployment MUST be documented and repeatable.
- A delivery that cannot be run outside the author's machine is incomplete.

**Why**: A Worker that only works in a demo is not a Digital FTE.

### 13. Maintainable and Understandable Code

Code is written for humans first; clarity beats cleverness.

- Code MUST be readable, with clear naming and minimal incidental complexity.
- Avoid unnecessary complexity, premature abstraction, and unrelated features.
- Prefer the smallest viable change; do not refactor unrelated code.
- New code MUST match surrounding style and idiom.

**Why**: Maintainable code is what makes the project a durable learning asset
and a safe base for an autonomous Worker.

### 14. Separation of Concerns

Specification, planning, implementation, and evaluation MUST remain distinct
and traceable to each other.

- Spec answers **WHAT/WHY**; Plan answers **HOW**; Tasks are the executable
  units; Implementation fulfills Tasks; Evaluation proves the Outcome.
- Each layer references the one above it for traceability.
- No layer MAY absorb the responsibility of another.

**Why**: Clean separation keeps decisions reviewable, reversible, and
traceable end-to-end.

## Lifecycle & Non-Negotiables

The following rules apply to every feature in this project, regardless of
scope.

- **No application features** are implemented before a ratified Specification
  and Plan exist.
- Every feature MUST have a clear Outcome and Acceptance Criteria recorded
  before work begins.
- Specification, Plan, and Tasks MUST be derived and approved in order; no
  skipping.
- AI Worker behavior MUST be deterministic where possible and evaluated with
  measurable criteria.
- Skills MUST contain reusable domain knowledge and operational instructions.
- Tools MUST have clear boundaries, permissions, inputs, outputs, and failure
  handling.
- External actions MUST follow least-privilege principles.
- Sensitive operations MUST support human approval or escalation.
- Secrets MUST NEVER be hardcoded or committed to Git.
- Changes MUST be testable and verifiable before merge.
- Avoid unnecessary complexity, premature abstraction, and unrelated features.
- Preserve traceability from business Outcome to Specification, Implementation,
  and Evaluation.

## Technology Context

This is a learning project on a Windows development environment. The following
stack is the default reference context for Specification, Plan, and Tasks:

- **OS / IDE**: Windows, VS Code
- **Version Control**: Git and GitHub
- **Languages**: Python 3.11+, Node.js
- **Package / Env**: `uv`
- **AI Tooling**: Claude Code, SpecifyPlus (SDD)
- **Containers**: Docker Desktop
- **Backend**: FastAPI
- **Frontend**: Next.js
- **Storage**: PostgreSQL

Use of this stack MUST be confirmed and justified in the Plan; alternatives are
allowed only with documented rationale in an ADR.

## Governance

- This Constitution supersedes all other development practices and informal
  guidance in this repository.
- **Amendment procedure**: Proposed changes are drafted, documented with
  rationale, reviewed, and adopted by the maintainer. Amendments MUST be
  recorded by bumping the Constitution Version and updating `Last Amended`.
- **Versioning policy**: Follows semantic versioning —
  MAJOR for principle removal/redefinition, MINOR for added or materially
  expanded principles/sections, PATCH for clarifications and wording fixes.
- **Compliance review**: Every Plan MUST pass the Constitution Check gate
  before research and be re-checked after design. PRs and reviews MUST verify
  compliance with these principles.
- **Documentation**: Use `.specify/memory/constitution.md` as the single source
  of truth for governing principles. Do not duplicate these rules in ad-hoc
  docs that can drift.

**Version**: 1.0.0 | **Ratified**: 2026-08-09 | **Last Amended**: 2026-08-09
