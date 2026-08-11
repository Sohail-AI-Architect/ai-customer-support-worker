"""Contract tests for POST /api/tickets (T034, US3).

Verifies the create contract: auth via X-Customer-Id, request body shape,
201 response with a ticket reference, and validation of required fields.
Data ownership/scoping is covered by integration tests (test_ticket_create.py).
"""

import uuid


def test_create_ticket_requires_customer_header(client):
    resp = client.post("/api/tickets", json={"subject": "S", "description": "D"})
    assert resp.status_code == 422  # missing required X-Customer-Id header


def test_create_ticket_returns_201_and_reference(client, session):
    from models.customer import Customer

    customer = Customer(external_id="contract-create-cust", name="Create Cust")
    session.add(customer)
    session.commit()
    session.refresh(customer)

    resp = client.post(
        "/api/tickets",
        headers={"X-Customer-Id": customer.external_id},
        json={"subject": "Broken checkout", "description": "Cannot complete purchase."},
    )
    assert resp.status_code == 201
    body = resp.json()
    for field in ("id", "subject", "status", "created_at"):
        assert field in body
    assert body["subject"] == "Broken checkout"
    assert body["status"] == "open"
    # id must be a valid UUID reference.
    uuid.UUID(body["id"])


def test_create_ticket_requires_subject(client, session):
    from models.customer import Customer

    customer = Customer(external_id="contract-create-cust2", name="Create Cust 2")
    session.add(customer)
    session.commit()
    session.refresh(customer)

    resp = client.post(
        "/api/tickets",
        headers={"X-Customer-Id": customer.external_id},
        json={"description": "No subject provided."},
    )
    assert resp.status_code == 422  # subject is required
