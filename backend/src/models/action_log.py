"""Worker action log (observability / audit)."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from db import Base


class WorkerActionLog(Base):
    __tablename__ = "worker_action_log"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    trace_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("conversations.id"), nullable=True
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    tool: Mapped[str | None] = mapped_column(String(100), nullable=True)
    input_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    outcome: Mapped[str] = mapped_column(
        String(20), default="ok"
    )  # ok | denied | error | escalated
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
