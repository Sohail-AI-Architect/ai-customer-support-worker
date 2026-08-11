---
id: 002
title: Plan AI Customer Support Worker
stage: plan
date: 2026-08-09
surface: agent
model: oc/deepseek-v4-flash-free
feature: 001-ai-support-worker
branch: 001-ai-support-worker
user: Sarah Sohail
command: /sp.plan
labels: [ai-worker, customer-support, digital-fte, plan, architecture, spec-driven-development]
links:
  spec: specs/001-ai-support-worker/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-ai-support-worker/plan.md
  - specs/001-ai-support-worker/research.md
  - specs/001-ai-support-worker/data-model.md
  - specs/001-ai-support-worker/quickstart.md
  - specs/001-ai-support-worker/contracts/openapi.yaml
  - specs/001-ai-support-worker/contracts/mcp-tools.md
  - history/prompts/001-ai-support-worker/002-plan-ai-customer-support-worker.plan.prompt.md
tests:
  - none (planning phase; test strategy defined in plan Section 24, evaluation harness planned in Sections 21-23)
---

## Prompt

Resume the interrupted /sp.plan workflow from the current repository state.

Inspect all files already created by the previous plan attempt before making changes.

Do not restart or duplicate existing work.

Complete all remaining plan-phase artifacts required by the SpecifyPlus workflow, including:
- plan.md
- research.md
- data-model.md
- API/contracts artifacts
- architecture/design decisions
- Constitution Check
- Specification Alignment Check
- PHR

Preserve valid work that already exists.

Do not implement application code.
Do not create implementation tasks yet.

When complete, summarize exactly which files were created or updated and confirm whether the plan is complete.

## Response snapshot

Resumed and completed the /sp.plan workflow on branch `001-ai-support-worker`. Inspected the existing state first: `plan.md` was still the untouched template (104 lines, placeholders intact) and `research.md`, `data-model.md`, `quickstart.md`, `contracts/` did not exist. Preserved the valid completed work (`spec.md`, `checklists/requirements.md`, spec PHR) and produced all missing plan-phase artifacts without duplicating anything.

Created/updated:
- `specs/001-ai-support-worker/plan.md` — comprehensive implementation plan (26 sections: architecture, folder structure, frontend, FastAPI backend, AI Worker, skills, tools, MCP mapping, data model, API boundaries, authN/authZ, hybrid authz, ticket ops create+read-only, approval/escalation, knowledge base, worker state, error handling, security, secrets, observability, evaluation, golden set/grader, containment metric, testing, Docker, deployment), plus request flow and approval/escalation flow diagrams, deferred-decisions-resolved, assumptions, risks, tradeoffs, 6 candidate architectural decisions, complexity tracking, and Constitution + Specification Alignment checks.
- `specs/001-ai-support-worker/research.md` — Phase 0, resolves the four deferred decisions (knowledge-base scope, tool-to-MCP mapping, escalation/approval UX, data retention) plus determinism, LLM choice, persistence, testing, and Docker research (Decision/Rationale/Alternatives).
- `specs/001-ai-support-worker/data-model.md` — Phase 1, PostgreSQL entities, fields, relationships, validation, state transitions, and authorization mappings.
- `specs/001-ai-support-worker/contracts/openapi.yaml` — REST API contract (customer + agent endpoints; no update/close/delete ticket endpoints).
- `specs/001-ai-support-worker/contracts/mcp-tools.md` — tool-to-MCP mapping and per-tool contracts with permissions and failure handling.
- `specs/001-ai-support-worker/quickstart.md` — local Docker/dev runbook.

Constitution Check: PASS (all 14 principles satisfied; multi-component web structure is inherent, not accidental — see Complexity Tracking). Specification Alignment: PASS (all FRs/NFRs, success metrics, and create+read-only ticket rule reflected). Six candidate ADRs identified (monorepo, worker-over-MCP, hybrid authz, create+read-only tickets, separate MCP servers, evaluation-first) — not auto-created per constitution.

Also ran `update-agent-context.ps1 -AgentType claude`; it only prepended a UTF-8 BOM to CLAUDE.md (no content inserted — no marker section exists) so I restored CLAUDE.md to keep the diff clean; the stack is documented in plan.md/research.md. No implementation code and no tasks were created.

## Outcome

- ✅ Impact: Delivered the full implementation plan and supporting design artifacts, satisfying the Constitution Check gate and Specification Alignment, ready for /sp.tasks.
- 🧪 Tests: none (planning phase); testing/evaluation strategy designed in plan Sections 21-24.
- 📁 Files: plan.md, research.md, data-model.md, quickstart.md, contracts/openapi.yaml, contracts/mcp-tools.md created; PHR created.
- 🔁 Next prompts: /sp.tasks to derive implementation tasks from this plan (then /sp.clarify only if needed).
- 🧠 Reflection: Resuming required first inspecting state to avoid duplicating the spec work; plan.md was still a template, so all plan artifacts were generated fresh. The update-agent-context script produced only a BOM in CLAUDE.md (no marker section), so I reverted it to keep the tree clean and rely on plan/research docs.

## Evaluation notes (flywheel)

- Failure modes observed: update-agent-context.ps1 reported "added language/framework/database" but actually only prepended a UTF-8 BOM to CLAUDE.md (no content markers existed); verified via git diff and restored the file. Earlier create-new-feature.ps1 hit a Join-Path 4-arg error on Windows PowerShell 5.1.
- Graders run and results (PASS/FAIL): N/A (planning phase). Constitution and spec-alignment checks passed by inspection.
- Prompt variant (if applicable): /sp.plan resume-withinspect (state-preserving continuation).
- Next experiment (smallest change to try): Proceed to /sp.tasks, deriving tasks from plan.md sections and resolving the exact MVP task scope.
