"""Integration tests: chat-level US3 ticket creation (session-scoped).

A customer asking to create a ticket gets a confirmation with a ticket
reference through the chat API, and the new ticket is owned by them. Requests
to modify an existing ticket are escalated, never honored (FR-011).
"""


def test_chat_creates_ticket_and_confirms(client, session):
    from models.customer import Customer

    customer = Customer(external_id="chat-create-owner", name="Chat Create")
    session.add(customer)
    session.commit()
    session.refresh(customer)

    resp = client.post(
        "/api/chat",
        headers={"X-Customer-Id": customer.external_id},
        json={"message": "I need to create a ticket, my laptop screen is broken."},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["intent"] == "create_ticket"
    assert body["escalated"] is False
    assert "created" in body["reply"].lower()
    assert "reference" in body["reply"].lower()

    # The new ticket is visible on the customer's account.
    tickets = client.get(
        "/api/tickets", headers={"X-Customer-Id": customer.external_id}
    )
    assert tickets.status_code == 200
    assert len(tickets.json()) >= 1


def test_chat_escalates_ticket_modify_request(client, session):
    from models.customer import Customer

    customer = Customer(external_id="chat-modify-cust", name="Chat Modify")
    session.add(customer)
    session.commit()
    session.refresh(customer)

    resp = client.post(
        "/api/chat",
        headers={"X-Customer-Id": customer.external_id},
        json={"message": "Please close my ticket #99."},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["escalated"] is True
    assert "human" in body["reply"].lower()
