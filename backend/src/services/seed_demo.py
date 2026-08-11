"""Seed demo users for the local MVP (T048, plan Section 16).

Creates a demo human agent (role=agent) so the agent queue UI can resolve
escalations. The demo agent id is exposed to the frontend via
NEXT_PUBLIC_AGENT_USER_ID. Idempotent on username.
"""

from __future__ import annotations

from sqlalchemy import select

from db import SessionLocal
from models.user import User

DEMO_AGENT_USERNAME = "demo-agent-1"


def seed_demo_agent(username: str = DEMO_AGENT_USERNAME) -> User:
    db = SessionLocal()
    try:
        user = db.scalar(select(User).where(User.username == username))
        if user is None:
            user = User(username=username, role="agent")
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
    finally:
        db.close()


if __name__ == "__main__":
    user = seed_demo_agent()
    print(f"Seeded demo agent: id={user.id} username={user.username} role={user.role}")
