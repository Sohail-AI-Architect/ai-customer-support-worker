"""Approved Knowledge Lookup skill (spec Section 8, plan Section 6).

Reusable domain knowledge: retrieve and apply the approved answer for a common
question. Refuses to answer when no approved source matches (never fabricates).
"""

from dataclasses import dataclass

from services.knowledge import best_match


@dataclass
class KnowledgeLookupResult:
    found: bool
    answer: str | None = None
    question: str | None = None


class ApprovedKnowledgeLookupSkill:
    name = "approved_knowledge_lookup"

    def __init__(self, db) -> None:
        self.db = db

    def run(self, query: str) -> KnowledgeLookupResult:
        article = best_match(self.db, query)
        if article is None:
            return KnowledgeLookupResult(found=False)
        return KnowledgeLookupResult(found=True, answer=article.answer, question=article.question)
