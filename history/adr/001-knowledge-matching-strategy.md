# ADR-001: Approved-Knowledge Matching Strategy

> **Scope**: Document the decision cluster for how the Worker matches a customer
> question to an approved knowledge article and decides when to refuse/escalate.
> This covers the matching algorithm, the confidence gate, and the absence of a
> vector store for the MVP.

- **Status:** Accepted
- **Date:** 2026-08-09
- **Feature:** 001-ai-support-worker
- **Context:** The AI Customer Support Worker (US1, P1 MVP) must answer common,
  low-risk questions ONLY from an approved knowledge base and never fabricate
  (FR-003/004/005; plan Section 15). The starter set is small (4 FAQ articles)
  and admin-maintained. The Worker must be deterministic where possible
  (NFR-005) and its behavior verified by a golden eval set. The key question is
  how to turn a free-text customer question into a confident, approved answer —
  and, equally important, how to recognize when no approved answer exists and
  refuse/escalate instead of guessing.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? Yes —
        retrieval correctness directly determines containment and accuracy
        success metrics (SC-001/SC-002), and is a cross-cutting concern across
        all future user stories that retrieve data.
     2) Alternatives: Multiple viable options considered with tradeoffs? Yes —
        keyword relevance scoring, embedding/vector search, LLM re-rank, exact
        FAQ match.
     3) Scope: Cross-cutting concern (not an isolated detail)? Yes — the same
        decision governs knowledge lookup now and customer/ticket retrieval in
        US2/US3. -->

## Decision

- **Matching algorithm:** token-based **relevance scoring** over the approved
  `knowledge_articles` table. Each meaningful query token (len ≥ 4, stop-words
  excluded) scores an article on question / keyword / answer hits
  (weights 3/2/1). Articles are ranked by descending score, most-recent first
  on ties.
- **Confidence gate:** `best_match` returns an article only if its score meets a
  minimum threshold (`MIN_MATCH_SCORE = 1`); otherwise it returns no match and
  the Worker refuses/escalates. This is the fabrication guard.
- **Storage & retrieval stack:** PostgreSQL `knowledge_articles` table
  (ARRAY keywords column), SQLAlchemy query, **no vector store** in the MVP.
- **Determinism:** the whole pipeline is deterministic (no LLM call in the
  match path), so the same question always yields the same classification and
  answer — verifiable by the golden eval set and unit tests.

## Consequences

### Positive

- **Never-fabricate guarantee** is enforced structurally: no match → no answer.
- **Deterministic and testable**: identical input → identical output; unit,
  contract, and integration tests assert exact behavior; golden eval is stable.
- **Zero additional infrastructure**: reuses the existing PostgreSQL/SQLAlchemy
  stack — no embedding model, index, or vector database to operate for the MVP.
- **Simple, auditable, least-privilege**: plain SQL, admin-maintained approved
  articles only; easy to reason about and hard to surprise.
- **Cheap and fast**: low latency (well under the ~15s SC-007 budget).

### Negative

- **Brittle to phrasing**: synonyms and reworded questions may miss or
  mis-rank an article without explicit keywords — recall is bounded by keyword
  coverage. Mitigation: keywords are curated per article and can be extended.
- **Not semantic**: no understanding of meaning; common-token false positives
  must be controlled via stop-words and the confidence threshold (a real bug
  this design had to fix during implementation).
- **Scales poorly to large KBs**: linear scan of approved articles per query;
  acceptable for a starter set, but a larger base would need indexing or
  embedding retrieval.

## Alternatives Considered

- **Alternative A — Embedding / vector search** (e.g., pgvector + a hosted
  embedding model): semantic matching handles paraphrase well and scales to
  large KBs. **Rejected for MVP:** adds a model dependency, embedding index, and
  non-determinism/latency that complicate the deterministic eval loop; overkill
  for a 4-article starter set. Revisit when KB grows or recall metrics degrade.
- **Alternative B — LLM re-ranking/classification**: pass the question to an LLM
  to select the best article. **Rejected for MVP:** non-deterministic, higher
  latency and cost, and it reintroduces a fabrication surface — the Worker
  could "find" an answer where none exists. Kept as a possible post-eval
  refinement behind the deterministic gate.
- **Alternative C — Exact FAQ string match only:** simplest, fully
  deterministic, but far too brittle — any rephrasing yields "no match" and
  poor containment. **Rejected:** unacceptable recall for a customer-facing
  worker.

## References

- Feature Spec: `specs/001-ai-support-worker/spec.md` (FR-003/004/005; SC-001/002/003/007)
- Implementation Plan: `specs/001-ai-support-worker/plan.md` (Section 15 Approved
  Knowledge-Base Design; Section 24 evaluation-first)
- Related ADRs: none
- Evaluator Evidence: `history/prompts/001-ai-support-worker/004-implement-ai-customer-support-worker.implement.prompt.md`
  (US1 golden eval 3/6 → 6/6 after first-token-only and stop-word bugs were
  fixed by this relevance-scoring design)
