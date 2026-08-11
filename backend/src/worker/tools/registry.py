"""Tool contract registry (constitution Principle 5, plan Section 7).

Each tool declares its name, input/output schema, permission scope, and failure
behavior. Tools are the Worker's only way to act; authorization is enforced
before a tool executes.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


class ToolError(Exception):
    """Structured tool failure (never raised out of bounds; surfaced as a result)."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass
class Tool:
    name: str
    description: str
    permission: str
    input_schema: dict[str, Any] = field(default_factory=dict)
    handler: Callable[..., Any] | None = None

    def run(self, **kwargs: Any) -> Any:
        if self.handler is None:
            raise ToolError("not_implemented", f"tool {self.name} has no handler")
        return self.handler(**kwargs)


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def list(self) -> list[Tool]:
        return list(self._tools.values())
