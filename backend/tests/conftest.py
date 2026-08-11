"""Shared test fixtures.

US1 tests run against a real PostgreSQL (the knowledge service uses
PostgreSQL-specific SQL: ARRAY + any(), ilike). The postgres service is started
via `docker compose up -d postgres`; tests create tables and seed approved
knowledge on the fly so they are self-contained.
"""

import pytest
from fastapi.testclient import TestClient

from db import Base, SessionLocal, engine
from main import app
from models.knowledge import KnowledgeArticle


@pytest.fixture(scope="session")
def db_engine():
    # Clean slate per test session: drop + recreate all tables so runs are
    # deterministic regardless of leftover rows (test isolation).
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield engine


@pytest.fixture()
def client(db_engine):
    yield TestClient(app)


@pytest.fixture()
def session(db_engine):
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def seed_approved_knowledge(session):
    """Seed a couple of approved articles; clean up afterwards."""

    articles = [
        KnowledgeArticle(
            question="What is your return policy?",
            answer="You may return eligible items within 30 days of delivery.",
            keywords=["return", "policy", "refund"],
            status="approved",
        ),
        KnowledgeArticle(
            question="How do I reset my password?",
            answer="Use the 'Forgot password' link on the login page.",
            keywords=["password", "reset", "forgot"],
            status="approved",
        ),
    ]
    for a in articles:
        session.add(a)
    session.commit()
    for a in articles:
        session.refresh(a)

    yield articles

    for a in articles:
        session.delete(a)
    session.commit()
