"""Integration tests for US2 authorization (T027).

Proves session scoping: an authenticated customer can read their OWN tickets,
and a request for ANOTHER customer's ticket is refused (no data returned).
This is the core US2 security requirement (spec FR-006, SC-005 no cross-customer
data).
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


def test_customer_reads_own_ticket(client, session):
    customer, ticket = _make_customer_with_ticket(
        session, "authz-own-customer", "My own order issue"
    )
    resp = client.get(
        f"/api/tickets/{ticket.id}", headers={"X-Customer-Id": customer.external_id}
    )
    assert resp.status_code == 200
    assert resp.json()["subject"] == "My own order issue"


def test_customer_cannot_read_another_customers_ticket(client, session):
    # Owner has the ticket; another customer must not be able to read it.
    owner, ticket = _make_customer_with_ticket(
        session, "authz-owner-customer", "Private ticket"
    )
    other = _make_customer_with_ticket(
        session, "authz-other-customer", "Other's ticket"
    )[0]

    resp = client.get(
        f"/api/tickets/{ticket.id}", headers={"X-Customer-Id": other.external_id}
    )
    assert resp.status_code == 403
    assert "unauthorized" in resp.json()["message"].lower()


def test_customer_list_only_sees_own_tickets(client, session):
    owner, _ = _make_customer_with_ticket(session, "authz-list-owner", "Own ticket A")
    _make_customer_with_ticket(session, "authz-list-other", "Not mine")
    _make_customer_with_ticket(session, "authz-list-owner2", "Own ticket B")

    # Add two tickets to the owner.
    from models.ticket import SupportTicket

    session.add(
        SupportTicket(customer_id=owner.id, subject="Own ticket B", description="d")
    )
    session.commit()

    resp = client.get("/api/tickets", headers={"X-Customer-Id": owner.external_id})
    assert resp.status_code == 200
    body = resp.json()
    subjects = [t["subject"] for t in body]
    assert "Own ticket A" in subjects
    assert "Not mine" not in subjects
