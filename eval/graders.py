"""Graders for the golden eval set (T015, US1).

Each grader inspects a WorkerResult and decides whether the case passed,
producing a graded record with a `pass` flag and human-readable reasons.

- intent_match: expected intent equals actual intent (when specified).
- escalated_match: expected escalated flag equals actual.
- reply_contains: every required substring appears in the reply.
"""

from __future__ import annotations

from typing import Any

# Result shape expected from the chat API (mirrors api/schemas.ChatResponse).
REQUIRED_FIELDS = ("reply", "intent", "escalated", "trace_id")


def grade(result: dict[str, Any], expected: dict[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    ok = True

    missing = [f for f in REQUIRED_FIELDS if f not in result]
    if missing:
        ok = False
        reasons.append(f"missing fields: {', '.join(missing)}")
        return {"pass": ok, "reasons": reasons}

    if "intent" in expected and result["intent"] != expected["intent"]:
        ok = False
        reasons.append(f"intent {result['intent']!r} != expected {expected['intent']!r}")

    if "escalated" in expected and result["escalated"] != expected["escalated"]:
        ok = False
        reasons.append(
            f"escalated {result['escalated']} != expected {expected['escalated']}"
        )

    for needle in expected.get("reply_contains", []):
        if needle.lower() not in result["reply"].lower():
            ok = False
            reasons.append(f"reply missing {needle!r}")

    if not reasons:
        reasons.append("all checks passed")
    return {"pass": ok, "reasons": reasons}
