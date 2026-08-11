---
id: 001
title: Establish AI FDE Lab Constitution
stage: constitution
date: 2026-08-09
surface: agent
model: oc/deepseek-v4-flash-free
feature: none
branch: master
user: Sarah Sohail
command: /sp.constitution
labels: [spec-driven-development, ai-worker, constitution, governance, learning-project]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
  - history/prompts/constitution/001-establish-ai-fde-lab-constitution.constitution.prompt.md
tests:
  - none (constitution-only; no code, spec, plan, or tasks created)
---

## Prompt

Create the project constitution for this AI FDE Lab project.

This project is a practical learning project based on the AI FDE / Agent Factory concepts we are studying. The purpose is to learn how to build a production-oriented Digital FTE / AI Worker through Spec-Driven Development.

Establish clear engineering principles for:

1. Spec-Driven Development
2. Outcome-first engineering
3. Digital FTE / AI Worker architecture
4. Reusable Skills and domain knowledge
5. Tools and MCP integrations
6. Evaluation-first development
7. Human-in-the-loop workflows
8. AI safety and governance
9. Security and least-privilege access
10. Testing and verification
11. Observability and traceability
12. Production readiness
13. Maintainable and understandable code
14. Clear separation between specification, planning, implementation, and evaluation

The project lifecycle must follow:

Outcome → Constitution → Specification → Plan → Tasks → Implementation → Evaluation → Verification → Deployment

Constitution requirements:

- Define principles that guide all future development.
- Prefer simple architecture suitable for learning while maintaining production-quality engineering practices.
- Every feature must have a clear outcome and acceptance criteria.
- Specifications must define WHAT and WHY before implementation.
- Plans must define HOW without prematurely implementing features.
- Tasks must be derived from the approved specification and plan.
- Implementation must follow the approved specification, plan, and tasks.
- AI Worker behavior must be deterministic where possible and evaluated with measurable criteria.
- Skills should contain reusable domain knowledge and operational instructions.
- Tools should have clear boundaries, permissions, inputs, outputs, and failure handling.
- External actions must follow least-privilege principles.
- Sensitive operations should support human approval or escalation.
- Secrets must never be hardcoded or committed to Git.
- Changes must be testable and verifiable.
- Avoid unnecessary complexity, premature abstraction, and unrelated features.
- Preserve traceability from business outcome to specification, implementation, and evaluation.

Technology context for this learning project:

- Windows development environment
- VS Code
- Git and GitHub
- Python 3.11+
- Node.js
- uv
- SpecifyPlus
- Claude Code
- Docker Desktop
- FastAPI
- Next.js
- PostgreSQL

Do not implement application features yet.

Do not create the specification, plan, tasks, or application code.

Only create or update the project constitution according to the project's existing SpecifyPlus structure.

After completing it, briefly report:
- where the constitution was created
- the principles established
- any important assumptions
- whether the project is ready for /sp.specify

## Response snapshot

Created/updated the project constitution at `.specify/memory/constitution.md`, ratifying it as **v1.0.0** (initial ratification; the template had never been filled).

Established 14 Core Principles, each declarative and testable: 1) Spec-Driven Development, 2) Outcome-First Engineering, 3) Digital FTE / AI Worker Architecture, 4) Reusable Skills and Domain Knowledge, 5) Tools and MCP Integrations, 6) Evaluation-First Development, 7) Human-in-the-Loop Workflows, 8) AI Safety and Governance, 9) Security and Least-Privilege Access, 10) Testing and Verification, 11) Observability and Traceability, 12) Production Readiness, 13) Maintainable and Understandable Code, 14) Separation of Concerns.

Added a "Lifecycle & Non-Negotiables" section codifying the mandated lifecycle (Outcome → Constitution → Specification → Plan → Tasks → Implementation → Evaluation → Verification → Deployment) plus all explicit constraints (no features before ratified spec/plan; deterministic, measurable AI Worker behavior; skills/tools boundaries; least-privilege; human approval for sensitive ops; no hardcoded secrets; testable changes; traceability). Added a "Technology Context" section capturing the Windows/VS Code/Git/GitHub/Python 3.11+/Node.js/uv/SpecifyPlus/Claude Code/Docker Desktop/FastAPI/Next.js/PostgreSQL stack as default reference. Added a Governance section with amendment procedure, semantic versioning policy, and compliance review expectations.

No spec, plan, tasks, or application code were created, per instructions.

## Outcome

- ✅ Impact: Ratified the project's governing constitution (v1.0.0) as the source of truth for all future SDD development; provides the principles and gates the Plan's Constitution Check must enforce.
- 🧪 Tests: none (document-only change; no runnable code).
- 📁 Files: `.specify/memory/constitution.md` created; PHR created.
- 🔁 Next prompts: /sp.specify to build the first feature specification against this constitution.
- 🧠 Reflection: Template placeholders fully resolved at ratification; no deferred items. Versioning/amendment rules now live in the Governance section.

## Evaluation notes (flywheel)

- Failure modes observed: Repo tree was read-only for the session user (dev-sohail) due to inherited ACLs; resolved by the user granting write access before writing the file. Write tool initially failed with EPERM on temp-file creation until permissions were restored.
- Graders run and results (PASS/FAIL): N/A (document-only).
- Prompt variant (if applicable): /sp.constitution with explicit 14-principle list and lifecycle mandate.
- Next experiment (smallest change to try): Proceed to /sp.specify for the first feature, verifying the Plan template's Constitution Check references these principles.
