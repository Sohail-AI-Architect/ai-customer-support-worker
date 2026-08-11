"""Integration tests: approval gate on sensitive/state-changing actions (T050, US5).

When the Worker proposes a sensitive or state-changing action, the chat API must
NOT execute it; instead it persists a pending ApprovalRequest for the
conversation so a human agent can approve or deny (plan Section 14, FR-014).
"""

from sqlalchemy import select

from models.approval import ApprovalRequest


def _chat(client, customer_id, message):
    return client.post(
        "/api/chat",
        headers={"X-Customer-Id": customer_id},
        json={"message": message},
    )


def _make_customer(session, external_id):
    from models.customer import Customer

    customer = Customer(external_id=external_id, name=f"Customer {external_id}")
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer


def test_sensitive_action_holds_pending_approval(client, session):
    customer = _make_customer(session, "appr-sensitive")
    resp = _chat(client, customer.external_id, "Can you cancel my subscription?")
    assert resp.status_code == 200
    body = resp.json()
    # The action is proposed for approval, not executed.
    assert body["approval_required"] is True

    # A pending approval record was persisted for the conversation.
    approvals = session.scalars(select(ApprovalRequest)).all()
    assert len(approvals) >= 1
    pending = approvals[-1]
    assert pending.status == "pending"
    assert pending.proposed_action != ""
    assert pending.decided_by is None


def test_irreversible_action_requests_approval(client, session):
    customer = _make_customer(session, "appr-irreversible")
    resp = _chat(client, customer.external_id, "Please delete my account.")
    assert resp.status_code == 200
    assert resp.json()["approval_required"] is True

    approvals = session.scalars(select(ApprovalRequest)).all()
    assert any(a.proposed_action != "" and a.status == "pending" for a in approvals)


def test_calm_request_does_not_request_approval(client, session):
    from models.knowledge import KnowledgeArticle
    from services.seed_knowledge import load_seed_data

    for item in load_seed_data():
        session.add(
            KnowledgeArticle(
                question=item["question"],
                answer=item["answer"],
                keywords=item.get("keywords", []),
                status="approved",
            )
        )
    session.commit()

    customer = _make_customer(session, "appr-calm")
    resp = _chat(client, customer.external_id, "What is your return policy?")
    assert resp.status_code == 200
    assert resp.json()["approval_required"] is False
