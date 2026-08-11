"""POST /api/chat — the Worker invocation path (US1)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_customer
from api.schemas import ChatRequest, ChatResponse
from db import get_db
from models.action_log import WorkerActionLog
from models.conversation import Conversation, ConversationMessage
from models.customer import Customer
from services.customer_data import CustomerDataServer
from services.escalation_approval import EscalationApprovalServer
from services.observability import new_trace_id
from worker.agent import WorkerAgent
from worker.skills.approval_protocol import ApprovalProtocolSkill
from worker.skills.customer_context import CustomerContextSkill
from worker.skills.escalation_triage import EscalationTriageSkill
from worker.skills.ticket_handling import TicketHandlingSkill

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    customer: Customer = Depends(get_customer),
    db: Session = Depends(get_db),
) -> ChatResponse:
    trace_id = new_trace_id()

    # Get or create the conversation (persisted state, plan Section 16).
    conversation = None
    if payload.conversation_id:
        conversation = db.get(Conversation, payload.conversation_id)
    if conversation is None:
        conversation = Conversation(customer_id=customer.id, channel="chat")
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # Persist the customer message.
    db.add(
        ConversationMessage(
            conversation_id=conversation.id,
            role="customer",
            content=payload.message,
            trace_id=trace_id,
        )
    )

    # Invoke the Worker with session-scoped skills (US2 retrieve, US3 create).
    data_server = CustomerDataServer(db, str(customer.id))
    skill = CustomerContextSkill(data_server)
    result = WorkerAgent(
        db,
        customer_context_skill=skill,
        ticket_handling_skill=TicketHandlingSkill(data_server),
    ).handle(payload.message, trace_id=trace_id)

    # Persist the worker reply and an audit action.
    db.add(
        ConversationMessage(
            conversation_id=conversation.id, role="worker", content=result.reply, trace_id=trace_id
        )
    )
    db.add(
        WorkerActionLog(
            trace_id=trace_id,
            conversation_id=conversation.id,
            action="worker.response",
            tool=None,
            outcome="escalated" if result.escalated else "ok",
        )
    )

    # US4: an escalated request is persisted as an open Escalation with context
    # so a human agent can see and resolve it (plan Section 14). The Worker
    # performs this via the escalation_triage skill on a session-scoped server.
    if result.escalated:
        esc_server = EscalationApprovalServer(db, str(customer.id))
        EscalationTriageSkill(esc_server).escalate(
            conversation_id=str(conversation.id),
            reason=result.reason or "escalated",
            context=payload.message,
        )

    # US5: a sensitive/state-changing action is proposed -> held pending human
    # approval, never executed (plan Section 14, FR-014). The Worker records an
    # approval_requests row via the approval_protocol skill on a session-scoped
    # server; a human approves or denies it later.
    if result.approval_required:
        ApprovalProtocolSkill(EscalationApprovalServer(db, str(customer.id))).request_approval(
            conversation_id=str(conversation.id),
            proposed_action=result.reason or "sensitive_action",
            payload={"message": payload.message},
        )

    db.commit()

    return ChatResponse(
        conversation_id=str(conversation.id),
        reply=result.reply,
        intent=result.intent,
        escalated=result.escalated,
        approval_required=result.approval_required,
        trace_id=trace_id,
    )
