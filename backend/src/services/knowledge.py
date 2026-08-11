"""Approved knowledge service.

The Worker answers ONLY from approved knowledge_articles (spec FR-003). When no
article is a confident match, the service returns no result so the Worker
refuses/escalates rather than fabricating (FR-004/005).

Matching is token-based relevance scoring (deterministic, per NFR-005): an
article scores points for each meaningful query token found in its question,
keywords, or answer. best_match only returns an article above a confidence
threshold, preventing common-token false positives.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.knowledge import KnowledgeArticle

# Min meaningful token length; ignores stop words and tiny fragments.
MIN_TOKEN_LEN = 4
STOP_WORDS = {
    "what",
    "which",
    "when",
    "where",
    "who",
    "whom",
    "whose",
    "how",
    "why",
    "this",
    "that",
    "these",
    "those",
    "there",
    "here",
    "with",
    "from",
    "have",
    "has",
    "been",
    "were",
    "will",
    "would",
    "could",
    "should",
    "shall",
    "about",
    "into",
    "your",
    "their",
    "them",
    "they",
    "then",
    "than",
    "know",
    "want",
    "need",
    "like",
    "tell",
}
# Min score for a match to be considered confident.
MIN_MATCH_SCORE = 1
# Boost weights per field hit.
QUESTION_WEIGHT = 3
KEYWORD_WEIGHT = 2
ANSWER_WEIGHT = 1


def _meaningful_tokens(query: str) -> list[str]:
    return [t for t in query.lower().split() if len(t) >= MIN_TOKEN_LEN and t not in STOP_WORDS]


def _score(article: KnowledgeArticle, tokens: list[str]) -> int:
    score = 0
    question = article.question.lower()
    keywords = [k.lower() for k in article.keywords]
    answer = article.answer.lower()
    for token in tokens:
        if token in question:
            score += QUESTION_WEIGHT
        if any(token in k for k in keywords):
            score += KEYWORD_WEIGHT
        if token in answer:
            score += ANSWER_WEIGHT
    return score


def search(db: Session, query: str, limit: int = 5) -> list[KnowledgeArticle]:
    """Return approved articles, best-scoring first (ties by most recent)."""
    tokens = _meaningful_tokens(query)
    stmt = select(KnowledgeArticle).where(KnowledgeArticle.status == "approved")
    candidates = db.scalars(stmt).all()
    if not tokens:
        return []
    scored = [(article, _score(article, tokens)) for article in candidates]
    scored = [(a, s) for a, s in scored if s > 0]
    scored.sort(key=lambda pair: (pair[1], pair[0].updated_at or pair[0].id), reverse=True)
    return [a for a, _ in scored[:limit]]


def best_match(db: Session, query: str) -> KnowledgeArticle | None:
    """Return the single best confident match, or None if none is confident."""
    results = search(db, query, limit=1)
    if not results:
        return None
    top = results[0]
    tokens = _meaningful_tokens(query)
    if _score(top, tokens) < MIN_MATCH_SCORE:
        return None
    return top
