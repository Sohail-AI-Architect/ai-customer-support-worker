"""Integration tests: chat-level US2 retrieval (session-scoped).

A customer asking about their own order gets their OWN ticket info through the
chat API; a cross-customer request is never answered with another customer's
data (the session-scoped CustomerDataServer refuses).
"""



def _make_customer_with_ticket(session, external_id, subject):
    from models.customer import Customer
    from models.ticket import SupportTicket

    customer = Customer(external_id=external_id, name=f"Customer {external_id}")
    session.add(customer)
    session.commit()
    session.refresh(customer)
    ticket = SupportTicket(customer_id=customer.id, subject=subject, description="details")
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return customer, ticket


def test_chat_returns_own_ticket_info(client, session):
    customer, ticket = _make_customer_with_ticket(
        session, "chat-retrieve-owner", "My laptop order"
    )
    resp = client.post(
        "/api/chat",
        headers={"X-Customer-Id": customer.external_id},
        json={"message": "What is the status of my order?"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["intent"] == "retrieve"
    assert body["escalated"] is False
    assert "My laptop order" in body["reply"]


def test_chat_refuses_when_no_customer_tickets(client, session):
    _make_customer_with_ticket(session, "chat-retrieve-empty", "Some ticket")
    _make_customer_with_ticket(session, "chat-retrieve-other", "Other's ticket")
    # This customer has NO tickets; requesting order status finds nothing.
    resp = client.post(
        "/api/chat",
        headers={"X-Customer-Id": "chat-retrieve-nobody"},
        json={"message": "What is the status of my order?"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["intent"] == "retrieve"
    assert "couldn't find any tickets" in body["reply"]
