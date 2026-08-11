"""AI Customer Support Worker agent (plan Section 5).

Deterministic-where-possible orchestrator: classify intent -> select skill ->
invoke tools -> build response -> decide (resolve / escalate / request approval).
For the MVP (US1), the agent answers from approved knowledge and never fabricates.

The agent is stateless across calls; conversation context is loaded by the API
layer from persisted state.
"""

from dataclasses import dataclass

from services.observability import new_trace_id
from worker.skills.approved_knowledge_lookup import ApprovedKnowledgeLookupSkill

# Keywords that make a request high-risk / sensitive -> escalate, never answer.
HIGH_RISK_KEYWORDS = [
    "refund",
    "payment",
    "cancel",
    "delete my",
    "account change",
    "personal data",
    "legal",
    "sue",
    "complaint",
]

# Phrases that ask about the customer's own orders/tickets -> retrieve (US2).
RETRIEVE_KEYWORDS = [
    "my order",
    "my tickets",
    "order status",
    "track my",
    "where is my order",
    "status of my order",
    "check the status",
]

# How-to questions ask for the *procedure* (covered by approved knowledge), not
# for the customer's specific data — these route to ANSWER, not RETRIEVE.
HOW_TO_PREFIXES = ("how can i", "how do i", "how to", "how would i")

# Requests to create a new ticket (US3) -> CREATE_TICKET.
CREATE_TICKET_KEYWORDS = [
    "create a ticket",
    "open a ticket",
    "file a ticket",
    "new ticket",
    "submit a ticket",
    "report a problem",
    "make a ticket",
]

# Sensitive/state-changing actions (US5, FR-014) the Worker may PROPOSE but must
# NOT execute until a human approves. Each maps to a canonical proposed_action
# label. Checked before HIGH_RISK so "cancel my account" gates approval rather
# than escalating; informational complaints (refund request, sue) still escalate.
APPROVAL_ACTIONS = [
    ("cancel my subscription", "cancel_subscription"),
    ("cancel my account", "cancel_account"),
    ("cancel my order", "cancel_order"),
    ("close my account", "close_account"),
    ("delete my account", "delete_account"),
    ("process a refund", "process_refund"),
    ("issue a refund", "issue_refund"),
    ("refund my order", "refund_order"),
    ("change my plan", "change_plan"),
    ("update my subscription", "update_subscription"),
    ("transfer my balance", "transfer_funds"),
]

# Requests to modify an existing ticket -> escalate, never honor (FR-011).
MODIFY_TICKET_KEYWORDS = [
    "close my ticket",
    "close the ticket",
    "delete my ticket",
    "update my ticket",
    "change the status",
    "close ticket",
    "update ticket",
    "delete ticket",
]


@dataclass
class WorkerResult:
    reply: str
    intent: str
    escalated: bool
    approval_required: bool
    trace_id: str
    reason: str | None = None


class Intent:
    ANSWER = "answer"
    RETRIEVE = "retrieve"
    ESCALATE = "escalate"
    OUT_OF_SCOPE = "out_of_scope"
    CREATE_TICKET = "create_ticket"
    APPROVE = "approval"


class WorkerAgent:
    def __init__(
        self,
        db,
        knowledge_skill=None,
        customer_context_skill=None,
        ticket_handling_skill=None,
    ) -> None:
        self.db = db
        self._knowledge_skill = knowledge_skill or ApprovedKnowledgeLookupSkill(db)
        self._customer_context_skill = customer_context_skill
        # No default: ticket creation needs a session-scoped data server, which
        # only the API layer can supply. Absent a skill, the agent refuses.
        self._ticket_handling_skill = ticket_handling_skill

    def handle(self, message: str, trace_id: str | None = None) -> WorkerResult:
        trace_id = trace_id or new_trace_id()
        intent, reason = self._classify(message)

        if intent == Intent.APPROVE:
            return WorkerResult(
                reply=(
                    "That action needs a human approval before I can take it. "
                    "I've submitted it for review — a support agent will let you "
                    "know once it's decided."
                ),
                intent=Intent.APPROVE,
                escalated=False,
                approval_required=True,
                trace_id=trace_id,
                reason=reason,
            )

        if intent == Intent.ESCALATE:
            return WorkerResult(
                reply="I've handed this to a human support agent who can help you.",
                intent=Intent.ESCALATE,
                escalated=True,
                approval_required=False,
                trace_id=trace_id,
                reason=reason,
            )

        if intent == Intent.OUT_OF_SCOPE:
            return WorkerResult(
                reply="I'm sorry, I can't help with that request. A human agent can assist you.",
                intent=Intent.OUT_OF_SCOPE,
                escalated=True,
                approval_required=False,
                trace_id=trace_id,
                reason=reason,
            )

        if intent == Intent.CREATE_TICKET:
            return self._handle_create_ticket(message, trace_id)

        if intent == Intent.RETRIEVE:
            return self._handle_retrieve(message, trace_id)

        # ANSWER: use approved knowledge, never fabricate.
        result = self._knowledge_skill.run(message)
        if result.found and result.answer:
            return WorkerResult(
                reply=result.answer,
                intent=Intent.ANSWER,
                escalated=False,
                approval_required=False,
                trace_id=trace_id,
            )

        # No approved answer -> refuse and escalate (FR-004/005).
        return WorkerResult(
            reply=(
                "I don't have an answer for that yet, but I've escalated it "
                "to a human agent to help you."
            ),
            intent=Intent.ESCALATE,
            escalated=True,
            approval_required=False,
            trace_id=trace_id,
            reason="unsupported",
        )

    def _classify(self, message: str) -> tuple[str, str | None]:
        lowered = message.lower()
        # US5: sensitive/state-changing actions are proposed -> human approval.
        for phrase, label in APPROVAL_ACTIONS:
            if phrase in lowered:
                return Intent.APPROVE, label
        for keyword in HIGH_RISK_KEYWORDS:
            if keyword in lowered:
                return Intent.ESCALATE, "high-risk/sensitive"
        # FR-011: modifying an existing ticket is never honored -> escalate.
        for keyword in MODIFY_TICKET_KEYWORDS:
            if keyword in lowered:
                return Intent.ESCALATE, "ticket_modify"
        for keyword in CREATE_TICKET_KEYWORDS:
            if keyword in lowered:
                return Intent.CREATE_TICKET, None
        if not lowered.startswith(HOW_TO_PREFIXES):
            for keyword in RETRIEVE_KEYWORDS:
                if keyword in lowered:
                    return Intent.RETRIEVE, None
        return Intent.ANSWER, None

    def _handle_create_ticket(self, message: str, trace_id: str) -> WorkerResult:
        """Create a ticket for the session customer via the ticket-handling skill.

        If no ticket-handling skill is wired (e.g., unit tests), we refuse
        rather than guess. A failed creation escalates to a human (FR-009 edge).
        """
        if self._ticket_handling_skill is None:
            return WorkerResult(
                reply="I'm sorry, I can't create a ticket for you right now.",
                intent=Intent.CREATE_TICKET,
                escalated=True,
                approval_required=False,
                trace_id=trace_id,
                reason="no_ticket_skill",
            )

        # Use the message itself as the ticket subject/description (bounded, no
        # fabrication): the worker creates a ticket describing the reported issue.
        result = self._ticket_handling_skill.create_ticket(
            subject=message[:255], description=message
        )
        if not result.ok or not result.ticket:
            return WorkerResult(
                reply=(
                    "I wasn't able to create your ticket, but I've escalated "
                    "this to a human agent to help you."
                ),
                intent=Intent.CREATE_TICKET,
                escalated=True,
                approval_required=False,
                trace_id=trace_id,
                reason="creation_failed",
            )

        reference = result.ticket.get("id")
        return WorkerResult(
            reply=f"Your ticket has been created (reference {reference}).",
            intent=Intent.CREATE_TICKET,
            escalated=False,
            approval_required=False,
            trace_id=trace_id,
        )

    def _handle_retrieve(self, message: str, trace_id: str) -> WorkerResult:
        """Answer a ticket/order-status question from the customer's OWN data.

        If no customer-context skill is wired (e.g., unit tests), we cannot
        safely retrieve, so we refuse rather than guess. Cross-customer access
        is refused by the session-scoped skill.
        """
        if self._customer_context_skill is None:
            return WorkerResult(
                reply="I'm sorry, I can't access account details for you right now.",
                intent=Intent.RETRIEVE,
                escalated=True,
                approval_required=False,
                trace_id=trace_id,
                reason="no_customer_context",
            )

        result = self._customer_context_skill.list_tickets()
        if not result.ok or not result.data or not result.data.get("tickets"):
            return WorkerResult(
                reply="I couldn't find any tickets on your account.",
                intent=Intent.RETRIEVE,
                escalated=False,
                approval_required=False,
                trace_id=trace_id,
            )

        tickets = result.data["tickets"]
        lines = ["Here are your recent tickets:"]
        for t in tickets[:5]:
            lines.append(f"- {t['subject']} ({t['status']})")
        return WorkerResult(
            reply="\n".join(lines),
            intent=Intent.RETRIEVE,
            escalated=False,
            approval_required=False,
            trace_id=trace_id,
        )
