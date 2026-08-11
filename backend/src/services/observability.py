"""Structured logging and traceability (constitution Principle 11, plan Section 20).

Every request and Worker action carries a trace_id so behavior can be replayed
and audited end-to-end.
"""

import logging
import uuid

import structlog

logger = structlog.get_logger()


def new_trace_id() -> str:
    return uuid.uuid4().hex


def configure_logging() -> None:
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.PrintLoggerFactory(),
    )
