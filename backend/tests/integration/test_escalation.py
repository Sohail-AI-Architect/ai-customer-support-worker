"""Integration tests: escalation on tricky requests (T042, US4).

When the Worker classifies a high-risk/sensitive/unsupported request, the chat
API must escalate AND persist an open Escalation record with context, linked to
the conversation, so a human agent can see it (plan Section 14).
"""

from sqlalchemy import select

from models.escalation import Escalation


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


def test_high_risk_message_escalates_and_persists(client, session):
    customer = _make_customer(session, "esc-high-risk")
    resp = _chat(client, customer.external_id, "I want to request a refund.")
    assert resp.status_code == 200
    assert resp.json()["escalated"] is True

    # An open escalation record was persisted for the conversation.
    escalations = session.scalars(select(Escalation)).all()
    assert len(escalations) >= 1
    esc = escalations[-1]
    assert esc.status == "open"
    assert esc.reason in ("high-risk/sensitive", "sensitive", "high-risk")
    assert esc.context != ""


def test_unsupported_request_escalates_and_persists(client, session):
    customer = _make_customer(session, "esc-unsupported")
    resp = _chat(client, customer.external_id, "Explain quantum flux capacitors.")
    assert resp.status_code == 200
    assert resp.json()["escalated"] is True

    escalations = session.scalars(select(Escalation)).all()
    assert len(escalations) >= 1
    assert escalations[-1].status == "open"


def test_non_escalated_message_creates_no_escalation(client, session):
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

    customer = _make_customer(session, "esc-calm")
    resp = _chat(client, customer.external_id, "What is your return policy?")
    assert resp.status_code == 200
    assert resp.json()["escalated"] is False

    escalations = session.scalars(select(Escalation)).all()
    assert not any(e.context == "What is your return policy?" for e in escalations)
