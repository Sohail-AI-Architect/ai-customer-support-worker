"""API dependencies: session/customer scoping and agent-role checks.

MVP simplification: the authenticated customer is identified by the
`X-Customer-Id` header, standing in for full session auth (T011 hardens this
with real session tokens). Data access remains scoped to this customer.
"""

import uuid

from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from db import get_db
from models.customer import Customer
from models.user import User


def get_customer(
    x_customer_id: str = Header(..., alias="X-Customer-Id"),
    db: Session = Depends(get_db),
) -> Customer:
    """Resolve the authenticated customer; create a placeholder if unknown."""
    try:
        ext_id = uuid.UUID(x_customer_id)
    except (ValueError, TypeError):
        ext_id = x_customer_id  # allow opaque external ids
    customer = db.scalar(select(Customer).where(Customer.external_id == str(ext_id)))
    if customer is None:
        customer = Customer(external_id=str(ext_id), name=f"customer-{ext_id}")
        db.add(customer)
        db.commit()
        db.refresh(customer)
    return customer


def require_agent(
    x_user_id: str = Header(..., alias="X-User-Id"),
    db: Session = Depends(get_db),
) -> User:
    """Require an agent/admin role for agent-facing endpoints.

    X-User-Id may be the user's UUID id or username (MVP convenience so a demo
    agent id works). Role check is always enforced.
    """
    try:
        ident = uuid.UUID(x_user_id)
    except (ValueError, TypeError):
        # Non-UUID value: treat X-User-Id as a username (demo convenience).
        user = db.scalar(select(User).where(User.username == x_user_id))
        if user is None or user.role not in {"agent", "admin"}:
            raise HTTPException(status_code=403, detail="agent role required") from None
        return user
    user = db.scalar(select(User).where(User.id == ident))
    if user is None or user.role not in {"agent", "admin"}:
        raise HTTPException(status_code=403, detail="agent role required")
    return user
