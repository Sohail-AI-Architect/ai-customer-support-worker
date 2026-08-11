"""Unit tests for the Worker agent core (US1 answering + escalation logic)."""

from worker.agent import Intent, WorkerAgent
from worker.skills.approved_knowledge_lookup import KnowledgeLookupResult


class _FakeKnowledgeSkill:
    def __init__(self, found: bool, answer: str | None = None) -> None:
        self._found = found
        self._answer = answer

    def run(self, query: str) -> KnowledgeLookupResult:
        if not self._found:
            return KnowledgeLookupResult(found=False)
        return KnowledgeLookupResult(found=True, answer=self._answer, question=query)


def test_answer_from_approved_knowledge() -> None:
    skill = _FakeKnowledgeSkill(found=True, answer="Return policy answer.")
    agent = WorkerAgent(db=None, knowledge_skill=skill)
    result = agent.handle("What is your return policy?")
    assert result.intent == Intent.ANSWER
    assert result.reply == "Return policy answer."
    assert result.escalated is False


def test_refuses_when_no_approved_answer() -> None:
    agent = WorkerAgent(db=None, knowledge_skill=_FakeKnowledgeSkill(found=False))
    result = agent.handle("Something not in the knowledge base.")
    assert result.escalated is True
    assert result.reason == "unsupported"
    assert "human" in result.reply.lower()


def test_escalates_high_risk_keyword() -> None:
    agent = WorkerAgent(db=None, knowledge_skill=_FakeKnowledgeSkill(found=True, answer="x"))
    result = agent.handle("I want to request a refund.")
    assert result.intent == Intent.ESCALATE
    assert result.escalated is True


def test_state_changing_action_requests_approval() -> None:
    # "cancel my account" is a sensitive/state-changing action (FR-014): the
    # Worker proposes it for approval rather than escalating or acting.
    agent = WorkerAgent(db=None, knowledge_skill=_FakeKnowledgeSkill(found=True, answer="x"))
    result = agent.handle("I want to cancel my account.")
    assert result.intent == Intent.APPROVE
    assert result.approval_required is True
    assert result.escalated is False


def test_retrieve_intent_without_context_skill_refuses() -> None:
    # No customer-context skill wired -> refuse, never guess.
    agent = WorkerAgent(db=None, knowledge_skill=_FakeKnowledgeSkill(found=False))
    result = agent.handle("What is the status of my order?")
    assert result.intent == Intent.RETRIEVE
    assert result.escalated is True
    assert result.reason == "no_customer_context"


def test_retrieve_returns_customer_tickets() -> None:
    class _FakeContextSkill:
        def list_tickets(self):
            class _R:
                ok = True
                data = {"tickets": [{"subject": "Order 1", "status": "open"}]}

            return _R()

    agent = WorkerAgent(
        db=None,
        knowledge_skill=_FakeKnowledgeSkill(found=False),
        customer_context_skill=_FakeContextSkill(),
    )
    result = agent.handle("What is the status of my order?")
    assert result.intent == Intent.RETRIEVE
    assert result.escalated is False
    assert "Order 1" in result.reply


def test_retrieve_no_tickets() -> None:
    class _FakeContextSkill:
        def list_tickets(self):
            class _R:
                ok = True
                data = {"tickets": []}

            return _R()

    agent = WorkerAgent(
        db=None,
        knowledge_skill=_FakeKnowledgeSkill(found=False),
        customer_context_skill=_FakeContextSkill(),
    )
    result = agent.handle("Track my order please.")
    assert result.intent == Intent.RETRIEVE
    assert "couldn't find any tickets" in result.reply


# --- US3: ticket creation ---


class _FakeTicketSkill:
    def __init__(self, ok: bool = True, reference: str | None = None) -> None:
        self._ok = ok
        self._reference = reference or "TKT-1001"

    def create_ticket(self, subject: str, description: str):
        class _R:
            pass

        r = _R()
        r.ok = self._ok
        r.ticket = (
            {"id": self._reference, "subject": subject, "status": "open"}
            if self._ok
            else None
        )
        r.reason = None if self._ok else "creation_failed"
        return r


def test_create_ticket_intent_creates_ticket() -> None:
    agent = WorkerAgent(
        db=None,
        knowledge_skill=_FakeKnowledgeSkill(found=False),
        ticket_handling_skill=_FakeTicketSkill(ok=True, reference="TKT-2001"),
    )
    result = agent.handle("I'd like to create a ticket about my broken laptop.")
    assert result.intent == Intent.CREATE_TICKET
    assert result.escalated is False
    assert "TKT-2001" in result.reply
    assert "create" in result.reply.lower() or "ticket" in result.reply.lower()


def test_create_ticket_requires_skill_refuses() -> None:
    # No ticket-handling skill wired -> refuse, never guess.
    agent = WorkerAgent(db=None, knowledge_skill=_FakeKnowledgeSkill(found=False))
    result = agent.handle("Please open a ticket for me.")
    assert result.intent == Intent.CREATE_TICKET
    assert result.escalated is True
    assert result.reason == "no_ticket_skill"


def test_create_ticket_failure_escalates() -> None:
    agent = WorkerAgent(
        db=None,
        knowledge_skill=_FakeKnowledgeSkill(found=False),
        ticket_handling_skill=_FakeTicketSkill(ok=False),
    )
    result = agent.handle("Create a ticket, the system is down.")
    assert result.intent == Intent.CREATE_TICKET
    assert result.escalated is True
    assert "human" in result.reply.lower()


def test_ticket_modify_request_escalates() -> None:
    # FR-011: requests to update/close/delete a ticket are never honored.
    agent = WorkerAgent(
        db=None,
        knowledge_skill=_FakeKnowledgeSkill(found=True, answer="x"),
        ticket_handling_skill=_FakeTicketSkill(ok=True),
    )
    result = agent.handle("Please close my ticket #123.")
    assert result.escalated is True
    assert result.reason == "ticket_modify"
