"""Contract tests for GET /api/tickets endpoints (T026, US2).

Verifies the request/response contract: auth via X-Customer-Id, list shape, and
per-item field structure. Data ownership/scoping is covered by the integration
tests (test_authorization.py).
"""



def test_list_tickets_requires_customer_header(client):
    resp = client.get("/api/tickets")
    assert resp.status_code == 422  # missing required X-Customer-Id header


def test_list_tickets_returns_200_and_list_shape(client, session):
    from models.customer import Customer

    customer = Customer(external_id="contract-ticket-cust", name="Contract Cust")
    session.add(customer)
    session.commit()
    session.refresh(customer)

    resp = client.get(
        "/api/tickets", headers={"X-Customer-Id": customer.external_id}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)


def test_ticket_detail_fields(client, session):
    from models.customer import Customer
    from models.ticket import SupportTicket

    customer = Customer(external_id="contract-ticket-cust2", name="Contract Cust 2")
    session.add(customer)
    session.commit()
    session.refresh(customer)
    ticket = SupportTicket(
        customer_id=customer.id, subject="Lost order", description="Where is my order?"
    )
    session.add(ticket)
    session.commit()
    session.refresh(ticket)

    resp = client.get(
        f"/api/tickets/{ticket.id}", headers={"X-Customer-Id": customer.external_id}
    )
    assert resp.status_code == 200
    body = resp.json()
    for field in ("id", "subject", "status", "created_at"):
        assert field in body
    assert body["subject"] == "Lost order"
