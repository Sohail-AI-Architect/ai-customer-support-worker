"""Seed the approved knowledge base from data/knowledge_seed.json (T014).

Run:  uv run python -m services.seed_knowledge
Requires the database schema to exist (apply Alembic migrations first).
"""

import json
from pathlib import Path

from config import get_settings
from db import SessionLocal
from models.knowledge import KnowledgeArticle


def load_seed_data() -> list[dict]:
    path = Path(get_settings().knowledge_seed_path)
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def seed() -> int:
    db = SessionLocal()
    count = 0
    try:
        for item in load_seed_data():
            article = KnowledgeArticle(
                question=item["question"],
                answer=item["answer"],
                keywords=item.get("keywords", []),
                status="approved",
            )
            db.add(article)
            count += 1
        db.commit()
    finally:
        db.close()
    return count


if __name__ == "__main__":
    print(f"Seeded {seed()} knowledge articles.")
