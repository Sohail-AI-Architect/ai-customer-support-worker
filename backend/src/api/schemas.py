"""Pydantic request/response schemas for the chat and ticket APIs."""

from pydantic import BaseModel, Field


class TicketCreateRequest(BaseModel):
    subject: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1, max_length=10000)


class ChatRequest(BaseModel):
    conversation_id: str | None = None
    message: str = Field(..., min_length=1, max_length=4000)


class ChatResponse(BaseModel):
    conversation_id: str
    reply: str
    intent: str
    escalated: bool
    approval_required: bool
    trace_id: str


class ApprovalDecisionRequest(BaseModel):
    decision: str = Field(..., description='"approved" or "denied"')
