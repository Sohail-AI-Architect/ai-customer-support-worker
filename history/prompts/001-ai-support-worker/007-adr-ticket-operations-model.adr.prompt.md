---
id: 007
title: ADR ticket operations model
stage: adr
date: 2026-08-09
surface: agent
model: oc/deepseek-v4-flash-free
feature: 001-ai-support-worker
branch: 001-ai-support-worker
user: Sarah Sohail
command: /sp.adr ticket-operations-model
labels: [ai-worker, customer-support, digital-fte, adr, ticket-operations, create-only, fr-010, fr-011]
links:
  spec: specs/001-ai-support-worker/spec.md
  ticket: null
  adr: history/adr/002-ticket-operations-model.md
  pr: null
files:
  - history/adr/002-ticket-operations-model.md
tests:
  - n/a (documentation only)
---

## Prompt

/sp.adr ticket-operations-model — Analyze planning artifacts and document
architecturally significant decisions as ADRs. Document the ticket operations
model decision cluster (create + read only, FR-010/FR-011, session scoping,
hybrid authorization) as an ADR following the 6-step workflow (load plan,
extract decision clusters, check existing ADRs, apply significance test, create
ADR, report). Create a PHR.

## Response snapshot

- Step 1: check-prerequisites.ps1 → FEATURE_DIR + plan.md present; existing ADRs:
  only ADR-001 (knowledge-matching).
- Step 2: extracted the ticket-operations cluster (create-only write surface,
  no update/close/delete, escalate-on-modify, session scoping, two-layer
  enforcement) from plan Sections 8/12/13 and spec US3 / FR-006/009/010/011.
- Step 4: significance test PASSED (impact, alternatives, cross-cutting scope).
- Step 5: create-adr.sh not present in repo → wrote ADR directly, matching the
  ADR-001 format, as `history/adr/002-ticket-operations-model.md`.
- Step 6: report — 1 ADR created, 1 existing referenced (no conflict).

## Outcome

- ✅ Impact: Documented the cross-cutting ticket write model decision (data
  model, REST + MCP tool surface, Worker classification, authorization).
- 🧪 Tests: n/a (documentation artifact).
- 📁 Files: history/adr/002-ticket-operations-model.md.
- 🔁 Next prompts: Proceed to Phase6 US4 (escalation) implementation per plan.
- 🧠 Reflection: No create-adr.sh script exists in this repo, so the ADR was
  authored directly following the established ADR-001 template/format rather
  than the scripted flow.

## Evaluation notes (flywheel)

- Failure modes observed: create-adr.sh absent (handled by direct authoring);
  plan.md present so no abort.
- Graders run and results (PASS/FAIL): ADR significance checklist all true
  (impact / alternatives / scope) — PASS.
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): none — documentation complete.
