"""Integration tests: ticket creation (T035, US3).

Covers the create path at the API layer: a customer can create a ticket on
their own account, the ticket is immediately readable via the scoped list/GET,
and cross-customer access to the new ticket is refused. No update/close/delete
routes exist (FR-010).
"""


def _make_customer(session, external_id):
    from models.customer import Customer

    customer = Customer(external_id=external_id, name=f"Customer {external_id}")
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer


def test_create_ticket_persists_and_readable(client, session):
    customer = _make_customer(session, "create-ticket-owner")
    resp = client.post(
        "/api/tickets",
        headers={"X-Customer-Id": customer.external_id},
        json={"subject": "Payment failed", "description": "Card declined."},
    )
    assert resp.status_code == 201
    created = resp.json()
    assert created["status"] == "open"

    # The created ticket is readable back through the scoped list.
    listed = client.get(
        "/api/tickets", headers={"X-Customer-Id": customer.external_id}
    )
    assert listed.status_code == 200
    assert any(t["id"] == created["id"] for t in listed.json())


def test_new_ticket_not_visible_cross_customer(client, session):
    owner = _make_customer(session, "create-ticket-owner2")
    resp = client.post(
        "/api/tickets",
        headers={"X-Customer-Id": owner.external_id},
        json={"subject": "Secret issue", "description": "Private details."},
    )
    assert resp.status_code == 201
    created = resp.json()

    # A different customer cannot see or read the new ticket.
    other = _make_customer(session, "create-ticket-other2")
    other_list = client.get(
        "/api/tickets", headers={"X-Customer-Id": other.external_id}
    )
    assert other_list.status_code == 200
    assert all(t["id"] != created["id"] for t in other_list.json())

    other_get = client.get(
        f"/api/tickets/{created['id']}", headers={"X-Customer-Id": other.external_id}
    )
    # Refused (4xx) — no data leak; 404 (not found) or 403 (forbidden) both safe.
    assert other_get.status_code in (403, 404)
    assert "Secret issue" not in other_get.text


def test_no_update_or_delete_routes(client, session):
    customer = _make_customer(session, "create-ticket-noroute")
    created = client.post(
        "/api/tickets",
        headers={"X-Customer-Id": customer.external_id},
        json={"subject": "S", "description": "D"},
    ).json()
    ticket_id = created["id"]

    # No PATCH/PUT/DELETE capability exists (FR-010).
    for method, path in (
        ("patch", f"/api/tickets/{ticket_id}"),
        ("put", f"/api/tickets/{ticket_id}"),
        ("delete", f"/api/tickets/{ticket_id}"),
    ):
        resp = getattr(client, method)(
            path, headers={"X-Customer-Id": customer.external_id}
        )
        assert resp.status_code == 405, f"{method.upper()} {path} should not exist"
