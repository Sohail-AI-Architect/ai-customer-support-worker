---
id: 005
title: ADR Knowledge Matching Strategy
stage: adr
date: 2026-08-09
surface: agent
model: oc/deepseek-v4-flash-free
feature: 001-ai-support-worker
branch: 001-ai-support-worker
user: Sarah Sohail
command: /sp.adr knowledge-matching-strategy
labels: [ai-worker, customer-support, digital-fte, adr, architecture, knowledge-retrieval]
links:
  spec: specs/001-ai-support-worker/spec.md
  ticket: null
  adr: history/adr/001-knowledge-matching-strategy.md
  pr: null
files:
  - history/adr/001-knowledge-matching-strategy.md
  - history/prompts/001-ai-support-worker/005-adr-knowledge-matching-strategy.adr.prompt.md
tests:
  - (ADR documents the eval-driven fix that took the US1 golden eval from 3/6 to 6/6; no new tests run)
---

## Prompt

/sp.adr knowledge-matching-strategy — the user accepted the ADR suggestion made
after the /sp.implement US1 MVP run and asked to document the decision to use
deterministic keyword relevance scoring (over embedding/vector search) for
approved-knowledge matching in the low-risk MVP.

Document this as a properly structured Architecture Decision Record: extract the
decision cluster (matching algorithm + confidence gate + storage stack +
determinism), apply the significance test, list alternatives with tradeoffs,
positive/negative consequences, and references linking back to plan/spec/eval.

## Response snapshot

Created `history/adr/001-knowledge-matching-strategy.md` (first ADR; no
history/adr/ dir existed, no create-adr.sh script present, so created
agent-natively from `.specify/templates/adr-template.md`).

The ADR documents the decision cluster:
- Matching: token-based relevance scoring (question/keyword/answer weights 3/2/1)
- Confidence gate: MIN_MATCH_SCORE=1 — no confident match → refuse/escalate
  (the never-fabricate guarantee)
- Stack: PostgreSQL knowledge_articles (ARRAY keywords), no vector store in MVP
- Determinism: no LLM in the match path → identical input → identical output

Alternatives considered (with rationale for rejection):
- A: Embedding/vector search (pgvector) — rejected for MVP (model dependency,
  non-determinism, infra; revisit as KB grows)
- B: LLM re-ranking — rejected for MVP (non-deterministic, fabrication surface)
- C: Exact FAQ string match — rejected (too brittle, poor recall)

Evidence cited: the eval-first loop that caught first-token-only matching and
stop-word false positives, taking US1 golden eval 3/6 → 6/6.

## Outcome

- ✅ Impact: Permanent, reviewable record of why deterministic keyword scoring
  was chosen, its tradeoffs, and the escape hatch (revisit vector search as KB
  grows) — protects future contributors from re-litigating the decision without
  context and aligns US2/US3 retrieval on the same cross-cutting approach.
- 🧪 Tests: N/A (documentation). References the eval evidence (US1 golden eval
  6/6).
- 📁 Files: history/adr/001-knowledge-matching-strategy.md created; PHR created.
- 🔁 Next prompts: continue /sp.implement (finish T019 MCP server + T024 chat
  UI, then Phases 4-8: US2-US5, Polish); consider ADRs for other candidate
  decisions in plan.md (hybrid authorization, stateless Worker, eval harness).
- 🧠 Reflection: No ADR script/template existed beyond the raw template — created
  the record agent-natively. Clustering the decision (algorithm + gate + stack +
  determinism) kept it a single meaningful ADR rather than several atomic ones.

## Evaluation notes (flywheel)

- Failure modes observed: no create-adr.sh script exists in this project, so the
  script-driven creation path was unavailable; created the ADR directly from the
  template instead (documented, non-blocking).
- Graders run and results (PASS/FAIL): Significance checklist PASS — cross-cutting
  (governs US1 knowledge + US2/US3 retrieval), multiple viable alternatives with
  tradeoffs, long-term impact on accuracy/containment metrics.
- Prompt variant (if applicable): /sp.adr with explicit decision title
  knowledge-matching-strategy.
- Next experiment (smallest change to try): write ADRs for the other candidate
  decisions already flagged in plan.md (hybrid authorization, stateless Worker,
  golden eval harness) so the record set is complete before deeper implementation.
