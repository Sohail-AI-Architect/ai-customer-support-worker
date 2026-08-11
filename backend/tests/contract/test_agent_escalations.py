"""Contract tests for agent escalation endpoints (T043, US4).

Verifies the agent-facing contract: agent role is required, listing open
escalations returns a list shape, and resolving marks an escalation closed.
"""


def _make_agent(session):
    import uuid

    from models.user import User

    user = User(username=f"agent-{uuid.uuid4().hex}", role="agent")
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def _make_escalation(session, reason="sensitive", context="Contract context"):
    import uuid

    from models.conversation import Conversation
    from models.customer import Customer
    from models.escalation import Escalation

    customer = Customer(external_id=f"agent-esc-{uuid.uuid4()}", name="Esc Cust")
    session.add(customer)
    session.commit()
    session.refresh(customer)
    conversation = Conversation(customer_id=customer.id, channel="chat")
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    escalation = Escalation(
        conversation_id=conversation.id, reason=reason, context=context, status="open"
    )
    session.add(escalation)
    session.commit()
    session.refresh(escalation)
    return escalation


def test_agent_escalations_requires_agent_role(client, session):
    import uuid

    from models.user import User

    # A non-agent user is refused (403).
    non_agent = User(username=f"customer-{uuid.uuid4().hex}", role="customer")
    session.add(non_agent)
    session.commit()
    session.refresh(non_agent)
    resp = client.get(
        "/api/agent/escalations", headers={"X-User-Id": str(non_agent.id)}
    )
    assert resp.status_code == 403


def test_agent_escalations_requires_user_header(client, session):
    # No X-User-Id header -> 422 (required header missing).
    resp = client.get("/api/agent/escalations")
    assert resp.status_code == 422


def test_agent_escalations_accepts_username(client, session):
    import uuid

    from models.user import User

    username = f"agent-{uuid.uuid4().hex}"
    user = User(username=username, role="agent")
    session.add(user)
    session.commit()
    session.refresh(user)
    _make_escalation(session)

    resp = client.get(
        "/api/agent/escalations", headers={"X-User-Id": username}
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_list_open_escalations_returns_200_list(client, session):
    agent = _make_agent(session)
    _make_escalation(session)

    resp = client.get(
        "/api/agent/escalations", headers={"X-User-Id": str(agent.id)}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert len(body) >= 1


def test_escalation_fields(client, session):
    agent = _make_agent(session)
    esc = _make_escalation(session, reason="unsupported", context="Needs human help.")

    resp = client.get(
        "/api/agent/escalations", headers={"X-User-Id": str(agent.id)}
    )
    assert resp.status_code == 200
    body = resp.json()
    item = next((e for e in body if e["id"] == str(esc.id)), None)
    assert item is not None
    for field in ("id", "reason", "context", "status", "created_at"):
        assert field in item
    assert item["reason"] == "unsupported"
    assert item["status"] == "open"


def test_resolve_escalation_marks_resolved(client, session):
    agent = _make_agent(session)
    esc = _make_escalation(session)

    resp = client.post(
        f"/api/agent/escalations/{esc.id}/resolve",
        headers={"X-User-Id": str(agent.id)},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "resolved"

    # It no longer appears in the open list.
    listed = client.get(
        "/api/agent/escalations", headers={"X-User-Id": str(agent.id)}
    )
    assert all(e["id"] != str(esc.id) for e in listed.json())
