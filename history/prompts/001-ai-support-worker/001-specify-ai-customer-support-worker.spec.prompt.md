---
id: 001
title: Specify AI Customer Support Worker
stage: spec
date: 2026-08-09
surface: agent
model: oc/deepseek-v4-flash-free
feature: 001-ai-support-worker
branch: 001-ai-support-worker
user: Sarah Sohail
command: /sp.specify
labels: [ai-worker, customer-support, digital-fte, spec, spec-driven-development]
links:
  spec: specs/001-ai-support-worker/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-ai-support-worker/spec.md
  - specs/001-ai-support-worker/checklists/requirements.md
  - history/prompts/001-ai-support-worker/001-specify-ai-customer-support-worker.spec.prompt.md
tests:
  - none (specification phase; tests defined in evaluation plan Section 15, to be built in later phases)
---

## Prompt

Create the first feature specification for this AI FDE Lab practical project.

We want to build a small but realistic AI Customer Support Digital FTE as a learning project.

The purpose is to practically understand how the AI FDE / Agent Factory approach works from business outcome to specification, planning, tasks, implementation, evaluation, and verification.

Business outcome:

Build an AI Customer Support Worker that can handle common, low-risk customer support requests using approved knowledge and tools, while recognizing situations that require human intervention.

The system should demonstrate the core concepts from our project constitution:

- Outcome-first engineering
- Digital FTE / AI Worker architecture
- Reusable Skills
- Tools
- MCP integrations where appropriate
- Evaluation-first development
- Human-in-the-loop workflows
- Security and least privilege
- Testing and verification
- Observability and traceability

The AI Worker should be able to:

- Understand customer support requests
- Answer common questions using approved support knowledge
- Retrieve relevant customer information when authorized
- Retrieve support ticket information
- Create a support ticket when appropriate
- Recognize ambiguous, unsupported, sensitive, or high-risk requests
- Escalate appropriate cases to a human
- Avoid taking sensitive or irreversible actions without human approval

Define the specification in terms of WHAT the system must accomplish and WHY.

Include:

1. Problem statement
2. Business outcome
3. Target users
4. User journeys
5. Functional requirements
6. Non-functional requirements
7. AI Worker responsibilities
8. Skills required
9. Tools required
10. MCP requirements, if justified
11. Data requirements
12. Human approval and escalation requirements
13. Security and authorization requirements
14. Safety and governance requirements
15. Evaluation requirements
16. Success metrics
17. Failure cases
18. Edge cases
19. Out-of-scope items
20. Acceptance criteria

Keep the specification technology-agnostic where possible.

Do not write implementation code.

Do not create the technical implementation plan yet.

Do not create implementation tasks yet.

Use the ratified constitution v1.0.0 as the governing project principles.

Before finalizing, check the specification against the constitution and identify any conflicts, missing requirements, assumptions, or unresolved decisions.

Create the specification and the appropriate PHR according to the existing SpecifyPlus workflow.

## Response snapshot

Created the first feature specification for the AI Customer Support Worker at `specs/001-ai-support-worker/spec.md` on branch `001-ai-support-worker`, governed by the ratified constitution v1.0.0. The spec is technology-agnostic (WHAT/WHY only; no implementation).

Resolved three high-impact scope decisions with the user before finalizing: (1) channel = interactive chat, (2) authorization = hybrid (session scoping for the customer + role-based limits on the Worker), (3) ticket operations = create + read only (never update/close/delete).

The spec covers all 20 requested sections: problem statement, business outcome, target users, 5 prioritized user journeys (MVP = answer common questions from approved knowledge; plus authorized info retrieval, ticket creation, escalation triage, and human-approval flows), 17 functional requirements, 7 non-functional requirements, AI Worker responsibilities (can/cannot), 5 required skills, 6 required tools, MCP justification, data requirements, human approval/escalation, security/authorization (least privilege, session scoping, no secrets), safety/governance, evaluation requirements (golden set + graders + containment metric), 7 measurable success metrics, failure cases, edge cases, out-of-scope items, and 9 acceptance criteria.

Also created `specs/001-ai-support-worker/checklists/requirements.md` (spec quality checklist — all items pass). Validation confirmed no [NEEDS CLARIFICATION] markers, no leftover placeholders, and no implementation-detail leaks. Constitution check: no conflicts identified; the spec aligns with all relevant principles (outcome-first, worker architecture, skills, tools, MCP, evaluation-first, human-in-the-loop, security/least-privilege, testing, observability/traceability, determinism, no secrets). Deferred items (knowledge-base scope, MCP server mapping, UX details, data retention) are recorded under "Unresolved Decisions" for the Plan phase.

## Outcome

- ✅ Impact: Delivered the ratified-constitution-compliant feature specification (WHAT/WHY) and its quality checklist, ready for /sp.clarify or /sp.plan.
- 🧪 Tests: none (specification phase); evaluation approach defined in Section 15 for later phases.
- 📁 Files: `specs/001-ai-support-worker/spec.md`, `specs/001-ai-support-worker/checklists/requirements.md`, PHR created.
- 🔁 Next prompts: /sp.plan to design HOW (tech stack, structure, tool/MCP mapping) without prematurely implementing.
- 🧠 Reflection: Asking the three scope questions up-front (channel/authz/ticket-ops) avoided placeholder markers and kept the spec decisive. The create-new-feature.ps1 script errored on `Join-Path` under Windows PowerShell 5.1 (needs pwsh 7); the prompts directory was created manually. Spec workflow kept technology-agnostic per constitution.

## Evaluation notes (flywheel)

- Failure modes observed: create-new-feature.ps1 failed on a 4-arg Join-Path call (Windows PowerShell 5.1 vs pwsh 7). Mitigated by manually creating the prompts dir and writing files directly.
- Graders run and results (PASS/FAIL): N/A (specification phase). Validation greps passed (no placeholders, no NEEDS CLARIFICATION, no impl leaks).
- Prompt variant (if applicable): /sp.specify with a structured 20-section feature description.
- Next experiment (smallest change to try): Proceed to /sp.plan; confirm the plan-template's Constitution Check references the ratified v1.0.0 principles.
