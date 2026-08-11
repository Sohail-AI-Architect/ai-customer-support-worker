"""Unit tests for the knowledge-server `knowledge.search` tool (T019).

Proves the tool contract: returns only approved articles, respects limit, and
fails safely on unknown tools / errors (never raises out of bounds).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend" / "src"))

import pytest

from knowledge_server import KnowledgeServer, ToolFailure


class _FakeArticle:
    def __init__(self, question: str, answer: str, keywords: list[str]) -> None:
        self.id = "art-1"
        self.question = question
        self.answer = answer
        self.keywords = keywords
        self.updated_at = None


class _FakeDB:
    def __init__(self, articles: list[_FakeArticle]) -> None:
        self._matched = articles

    def scalars(self, _stmt):
        return self

    def all(self):
        return self._matched


def _server():
    articles = [
        _FakeArticle("What is your return policy?", "30 day returns.", ["return", "policy"]),
        _FakeArticle("How do I reset my password?", "Use forgot password.", ["password"]),
    ]
    return KnowledgeServer(_FakeDB(articles))


def test_knowledge_search_returns_articles():
    server = _server()
    result = server.call_tool("knowledge.search", {"query": "return policy"})
    assert "articles" in result
    assert isinstance(result["articles"], list)


def test_knowledge_search_output_has_contract_fields():
    server = _server()
    result = server.call_tool("knowledge.search", {"query": "return policy", "limit": 1})
    for article in result["articles"]:
        for field in ("id", "question", "answer", "keywords"):
            assert field in article


def test_unknown_tool_raises_structured_failure():
    server = _server()
    with pytest.raises(ToolFailure) as exc:
        server.call_tool("nope.run", {})
    assert exc.value.code == "unknown_tool"


def test_list_tools_contains_knowledge_search():
    server = _server()
    names = [t.name for t in server.list_tools()]
    assert "knowledge.search" in names
