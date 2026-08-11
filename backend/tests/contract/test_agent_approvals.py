"""Contract tests for agent approval endpoints (T051, US5).

Verifies the agent-facing contract: agent role is required, listing pending
approvals returns a list shape, and approving/denying marks an approval
decided (409 if it is no longer pending).
"""

import uuid

from models.approval import ApprovalRequest


def _make_agent(session):
    from models.user import User

    user = User(username=f"agent-{uuid.uuid4().hex}", role="agent")
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def _make_approval(session, status="pending", proposed_action="cancel_subscription"):
    from models.conversation import Conversation
    from models.customer import Customer

    customer = Customer(external_id=f"appr-ag-{uuid.uuid4()}", name="Appr Cust")
    session.add(customer)
    session.commit()
    session.refresh(customer)
    conversation = Conversation(customer_id=customer.id, channel="chat")
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    approval = ApprovalRequest(
        conversation_id=conversation.id,
        proposed_action=proposed_action,
        payload={"message": "Cancel my subscription"},
        status=status,
    )
    session.add(approval)
    session.commit()
    session.refresh(approval)
    return approval


def test_approvals_require_agent_role(client, session):
    from models.user import User

    non_agent = User(username=f"customer-{uuid.uuid4().hex}", role="customer")
    session.add(non_agent)
    session.commit()
    session.refresh(non_agent)
    resp = client.get("/api/agent/approvals", headers={"X-User-Id": str(non_agent.id)})
    assert resp.status_code == 403


def test_approvals_requires_user_header(client):
    resp = client.get("/api/agent/approvals")
    assert resp.status_code == 422


def test_approvals_accepts_username(client, session):
    username = f"agent-{uuid.uuid4().hex}"
    from models.user import User

    user = User(username=username, role="agent")
    session.add(user)
    session.commit()
    session.refresh(user)
    _make_approval(session)

    resp = client.get("/api/agent/approvals", headers={"X-User-Id": username})
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_list_pending_approvals_returns_fields(client, session):
    agent = _make_agent(session)
    approval = _make_approval(session, proposed_action="delete_account")

    resp = client.get("/api/agent/approvals", headers={"X-User-Id": str(agent.id)})
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    item = next((a for a in body if a["id"] == str(approval.id)), None)
    assert item is not None
    for field in ("id", "proposed_action", "payload", "status"):
        assert field in item
    assert item["status"] == "pending"
    assert item["proposed_action"] == "delete_account"


def test_approve_marks_approved(client, session):
    agent = _make_agent(session)
    approval = _make_approval(session)

    resp = client.post(
        f"/api/agent/approvals/{approval.id}/decision",
        headers={"X-User-Id": str(agent.id)},
        json={"decision": "approved"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "approved"
    assert body["id"] == str(approval.id)


def test_deny_marks_denied(client, session):
    agent = _make_agent(session)
    approval = _make_approval(session)

    resp = client.post(
        f"/api/agent/approvals/{approval.id}/decision",
        headers={"X-User-Id": str(agent.id)},
        json={"decision": "denied"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "denied"


def test_decision_on_non_pending_returns_409(client, session):
    agent = _make_agent(session)
    approval = _make_approval(session, status="approved")

    resp = client.post(
        f"/api/agent/approvals/{approval.id}/decision",
        headers={"X-User-Id": str(agent.id)},
        json={"decision": "approved"},
    )
    assert resp.status_code == 409
