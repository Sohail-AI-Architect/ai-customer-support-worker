"""Integration tests for US1 answering/refusal through the chat API (T018).

Proves the end-to-end path: approved knowledge is returned verbatim, and an
unsupported question is not answered (Worker refuses/escalates rather than
fabricating). Both rely on the PostgreSQL-backed knowledge service.
"""



def test_answers_common_question_from_approved_knowledge(client, seed_approved_knowledge):
    resp = client.post(
        "/api/chat",
        headers={"X-Customer-Id": "integ-customer-1"},
        json={"message": "What is your return policy?"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["intent"] == "answer"
    assert body["escalated"] is False
    assert "30 days of delivery" in body["reply"]
    assert "You may return" in body["reply"]


def test_refuses_when_no_approved_answer(client, seed_approved_knowledge):
    resp = client.post(
        "/api/chat",
        headers={"X-Customer-Id": "integ-customer-2"},
        json={"message": "Explain the quantum flux capacitor mechanism."},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["escalated"] is True
    assert "human" in body["reply"].lower()


def test_escalates_sensitive_request(client, seed_approved_knowledge):
    resp = client.post(
        "/api/chat",
        headers={"X-Customer-Id": "integ-customer-3"},
        json={"message": "I want to request a refund for my order."},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["escalated"] is True
    assert "human" in body["reply"].lower()
