"""Contract tests for POST /api/chat (T017, US1).

Verifies the request/response contract: status codes, response schema shape,
and that a request flows through to a chat reply.
"""

from fastapi.testclient import TestClient


def _post_chat(client: TestClient, message: str, conversation_id: str | None = None):
    return client.post(
        "/api/chat",
        headers={"X-Customer-Id": "contract-customer-1"},
        json={"conversation_id": conversation_id, "message": message},
    )


def test_chat_returns_200_and_contract_shape(client, seed_approved_knowledge):
    resp = _post_chat(client, "What is your return policy?")
    assert resp.status_code == 200
    body = resp.json()
    for field in (
        "conversation_id",
        "reply",
        "intent",
        "escalated",
        "approval_required",
        "trace_id",
    ):
        assert field in body, f"missing field {field}"
    assert isinstance(body["conversation_id"], str)
    assert isinstance(body["trace_id"], str)
    assert body["reply"]


def test_chat_requires_customer_header(client):
    resp = client.post("/api/chat", json={"message": "hello"})
    assert resp.status_code == 422  # missing required X-Customer-Id header


def test_chat_rejects_empty_message(client):
    resp = client.post(
        "/api/chat",
        headers={"X-Customer-Id": "contract-customer-2"},
        json={"message": ""},
    )
    assert resp.status_code == 422


def test_chat_trace_header_present(client, seed_approved_knowledge):
    resp = _post_chat(client, "hello there")
    assert resp.status_code == 200
    assert "X-Trace-Id" in resp.headers
