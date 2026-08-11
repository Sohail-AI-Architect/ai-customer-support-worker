"""knowledge-server MCP server: exposes `knowledge.search` (T019, plan Section 8).

Read-only. Returns only approved knowledge articles. Implements the tool
contract registry so every tool declares its input/output schema, permission,
and failure handling (constitution Principle 5).

The server is framework-agnostic here for testability: a `KnowledgeServer`
class exposes `list_tools()` and `call_tool()`. An MCP transport (stdio/HTTP)
can be layered on later; the tool logic itself is the durable contract.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from services.knowledge import search

# Public to the Worker: approved knowledge is always readable (mcp-tools.md).
PERMISSION = "read"


@dataclass
class ToolSpec:
    name: str
    description: str
    input_schema: dict[str, Any] = field(default_factory=dict)


class ToolFailure(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


TOOL_SPECS: list[ToolSpec] = [
    ToolSpec(
        name="knowledge.search",
        description="Search approved knowledge articles by query text. Read-only.",
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Customer question text"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 20, "default": 5},
            },
            "required": ["query"],
        },
    ),
]


class KnowledgeServer:
    """Implements the knowledge MCP tool set against the approved knowledge base."""

    def __init__(self, db) -> None:
        self.db = db

    def list_tools(self) -> list[ToolSpec]:
        return TOOL_SPECS

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        try:
            if name == "knowledge.search":
                return self._knowledge_search(**arguments)
            raise ToolFailure("unknown_tool", f"unknown tool {name!r}")
        except ToolFailure:
            raise
        except Exception as exc:  # noqa: BLE001 - tools return structured errors
            raise ToolFailure("knowledge_unavailable", str(exc)) from exc

    def _knowledge_search(self, query: str, limit: int = 5) -> dict[str, Any]:
        articles = search(self.db, query, limit=limit)
        return {
            "articles": [
                {
                    "id": str(a.id),
                    "question": a.question,
                    "answer": a.answer,
                    "keywords": list(a.keywords),
                }
                for a in articles
            ]
        }
