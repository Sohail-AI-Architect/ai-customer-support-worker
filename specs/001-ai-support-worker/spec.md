# Feature Specification: AI Customer Support Worker

**Feature Branch**: `001-ai-support-worker`  
**Created**: 2026-08-09  
**Status**: Draft  
**Input**: User description (AI Customer Support Digital FTE as a learning project)

> **Governing principles**: This specification is governed by the ratified
> project constitution v1.0.0 (`.specify/memory/constitution.md`). It defines
> **WHAT** the system must accomplish and **WHY**; it intentionally avoids
> implementation details (frameworks, languages, data stores). Those are
> decided in the Plan phase.

---

## 1. Problem Statement

Customer support teams spend a large share of their effort on common, low-risk
requests that repeat with little variation — e.g., "what is your return policy?",
"how do I reset my password?", "where is my order?". Answering these manually is
slow for the customer and consumes expensive human attention that is better spent
on complex or sensitive cases.

For this learning project, we want to build a **Digital FTE / AI Customer Support
Worker** that handles these common, low-risk requests using **approved knowledge**
and **authorized tools**, while reliably recognizing when a request is ambiguous,
unsupported, sensitive, or high-risk and handing it to a human. The purpose is to
practically learn how the AI FDE / Agent Factory approach works end-to-end — from
business outcome through specification, planning, tasks, implementation,
evaluation, and verification — on a small but realistic system.

## 2. Business Outcome

Build an AI Customer Support Worker that resolves common, low-risk customer
support requests from **approved knowledge** using **authorized tools**, and that
**escalates to a human** whenever it cannot answer safely or is not authorized to
act. The Worker never fabricates answers and never takes sensitive or irreversible
actions without human approval.

Success for this outcome means: routine requests are handled instantly and
consistently, customers get faster answers, human agents spend their time on
complex/sensitive cases, and every Worker action is traceable and safe.

## 3. Target Users

- **Customers** — end users who send support requests and receive answers, ticket
  confirmations, or a hand-off to a human.
- **Human support agents** — people who review escalations and approve sensitive
  actions proposed by the Worker.
- **Support operations / administrators** — people who maintain the approved
  knowledge base, define what is in scope, review Worker behavior and metrics, and
  manage permissions.
- **The AI Worker itself** — the automated agent that interprets requests, applies
  skills and tools within its authorization, and decides when to escalate.

## 4. User Journeys

User stories are ordered as independently testable slices so each can ship as a
usable increment. P1 is the MVP.

### User Story 1 — Answer common questions (Priority: P1) 🎯 MVP

A customer asks a common, low-risk question. The Worker answers from approved
support knowledge.

**Why this priority**: Answering common questions from approved knowledge is the
highest-value, lowest-risk capability and the foundation everything else builds on.

**Independent Test**: A customer sends a question whose answer exists in the
approved knowledge base; the Worker returns the correct, approved answer and does
not consult any customer data or ticket systems.

**Acceptance Scenarios**:
1. **Given** a customer asks a common question covered by approved knowledge,
   **When** the Worker processes it, **Then** the customer receives the correct
   approved answer.
2. **Given** the customer asks a question **not** covered by approved knowledge,
   **When** the Worker processes it, **Then** the Worker does NOT invent an answer
   and instead states it cannot answer or escalates.

### User Story 2 — Retrieve authorized customer/ticket info (Priority: P2)

A customer asks about their own account or ticket. The Worker retrieves the
information **only when authorized** and **only for the authenticated customer**.

**Why this priority**: Personal data access is the first place authorization
matters; scoping to the authenticated customer demonstrates least-privilege access.

**Independent Test**: An authenticated customer asks for their own ticket status;
the Worker returns the accurate status from the ticket system. Asking for another
customer's data is refused.

**Acceptance Scenarios**:
1. **Given** an authenticated customer asks about their own ticket, **When** the
   Worker retrieves it, **Then** it returns accurate information scoped to that
   customer.
2. **Given** the request refers to another customer's data, **When** the Worker
   checks authorization, **Then** it refuses and does not retrieve the data.

### User Story 3 — Create a support ticket (Priority: P3)

A customer describes a problem that warrants a new ticket. The Worker creates a
support ticket and confirms it.

**Why this priority**: Creating a ticket is the first authorized write action and
tests that the Worker can take bounded, low-risk action.

**Independent Test**: A customer reports an issue; the Worker creates a ticket and
returns a confirmation with a ticket reference. The Worker cannot update, close,
or delete existing tickets.

**Acceptance Scenarios**:
1. **Given** a customer reports a valid issue, **When** the Worker creates a
   ticket, **Then** it returns a confirmation with a ticket reference.
2. **Given** a ticket already exists and the customer asks to change its status,
   **When** the Worker processes the request, **Then** it does NOT modify the
   existing ticket and instead escalates or defers to a human.

### User Story 4 — Recognize and escalate tricky requests (Priority: P4)

A customer makes an ambiguous, unsupported, sensitive, or high-risk request. The
Worker recognizes it and escalates to a human instead of answering or acting.

**Why this priority**: Safe failure is central to the constitution's
human-in-the-loop and safety principles; it must exist before real usage.

**Independent Test**: A sensitive or high-risk request is routed to the human
queue with context and is not answered directly by the Worker.

**Acceptance Scenarios**:
1. **Given** a sensitive or high-risk request, **When** the Worker classifies it,
   **Then** it does NOT answer or act directly and escalates to a human with
   context.
2. **Given** an ambiguous request, **When** the Worker cannot determine intent,
   **Then** it asks a clarifying question or escalates rather than guessing.

### User Story 5 — Human approval for sensitive actions (Priority: P4)

When the Worker identifies an action that is sensitive or state-changing, it
requests human approval and does not execute until approved.

**Why this priority**: This directly implements the constitution's requirement
that sensitive operations support human approval.

**Independent Test**: The Worker proposes a sensitive action, it is held pending
approval, and it is not executed until a human approves it.

**Acceptance Scenarios**:
1. **Given** the Worker proposes a sensitive action, **When** it reaches an
   approval gate, **Then** the action is held and not executed until approved.
2. **Given** a human denies the action, **When** the denial is recorded, **Then**
   the Worker does not execute it and informs the customer appropriately.

### Edge Cases

- The customer is not authenticated or authorization cannot be verified.
- The request references data for a customer other than the authenticated one.
- The approved knowledge base has no match for the question.
- The ticket system is unavailable or a ticket creation fails.
- The customer sends multiple intents in one message.
- The customer is abusive or requests an out-of-scope action.
- The message is empty, extremely long, or not in a supported language.

---

## 5. Functional Requirements

### 5.1 Request Understanding

- **FR-001**: The Worker MUST understand and classify the intent of a customer
  support request (e.g., answer question, retrieve info, create ticket, escalate).
- **FR-002**: The Worker MUST maintain conversation context across the chat session
  so follow-up messages are interpreted in context.

### 5.2 Answering from Approved Knowledge

- **FR-003**: The Worker MUST answer common questions **only** from approved
  support knowledge.
- **FR-004**: The Worker MUST NOT fabricate facts, prices, policies, or promises.
- **FR-005**: When the Worker cannot answer from approved knowledge, it MUST NOT
  guess; it MUST state it cannot answer and/or escalate.

### 5.3 Authorized Data Access

- **FR-006**: The Worker MUST retrieve customer account information **only** when
  authorized and **only** for the authenticated customer.
- **FR-007**: The Worker MUST retrieve ticket information only when authorized.
- **FR-008**: The Worker MUST refuse access to another customer's data.

### 5.4 Ticket Handling

- **FR-009**: The Worker MUST create a support ticket when appropriate and return a
  confirmation with a ticket reference.
- **FR-010**: The Worker MUST NOT update, close, or delete existing tickets
  (create + read only).
- **FR-011**: When a customer requests a ticket operation the Worker may not
  perform, the Worker MUST escalate or defer to a human.

### 5.5 Recognition, Escalation, and Approval

- **FR-012**: The Worker MUST detect ambiguous, unsupported, sensitive, or
  high-risk requests.
- **FR-013**: The Worker MUST escalate to a human with sufficient context
  (conversation summary, reason, and relevant authorized data) when required.
- **FR-014**: The Worker MUST request human approval before any sensitive or
  irreversible action and MUST NOT execute it until approved.
- **FR-015**: The Worker MUST record the approval decision (approved / denied) and
  act only in accordance with it.

### 5.6 Safety and Observability

- **FR-016**: The Worker MUST log every action, decision, and data access for
  traceability and audit.
- **FR-017**: The Worker MUST handle out-of-scope or abusive requests gracefully
  without harm and without fabricating answers.

## 6. Non-Functional Requirements

- **NFR-001 (Performance)**: The Worker MUST respond to a chat message within a
  reasonable latency for interactive support (target: user perceives a timely
  reply, ~15 seconds p95).
- **NFR-002 (Availability)**: The system MUST remain available during supported
  support hours, with a defined degradation behavior when a dependency fails.
- **NFR-003 (Security)**: The Worker MUST follow least-privilege access; secrets
  MUST never be hardcoded; all data access MUST be authorized and audited.
- **NFR-004 (Observability)**: The Worker MUST emit structured, actionable logs
  and MUST support replay and audit of its behavior.
- **NFR-005 (Determinism)**: The Worker's classification and decisions MUST be
  reproducible and evaluable; the same request MUST yield the same classification
  where possible.
- **NFR-006 (Testability)**: Every functional requirement MUST have a corresponding
  automated test or verification path.
- **NFR-007 (Traceability)**: Every action MUST be traceable from business outcome
  through specification, implementation, and evaluation.

## 7. AI Worker Responsibilities

**The Worker MUST:**

- Interpret and classify customer requests.
- Answer only from approved support knowledge; never fabricate.
- Retrieve authorized customer/ticket data only when permitted and only for the
  authenticated customer.
- Create support tickets when appropriate.
- Recognize ambiguous, unsupported, sensitive, or high-risk requests.
- Escalate to a human with context when it cannot safely answer or act.
- Request human approval for sensitive/irreversible actions and wait for the
  outcome.
- Log all actions and decisions.

**The Worker MUST NOT:**

- Invent facts, prices, policies, or promises.
- Access another customer's data.
- Update, close, or delete existing tickets.
- Take sensitive or irreversible actions without human approval.
- Act outside its defined authorization boundary.

## 8. Skills Required

Skills package reusable domain knowledge and operational instructions. The
following skills are required (each MUST declare inputs, outputs, and when it
applies):

- **Approved Knowledge Lookup** — retrieve and apply the approved answer for a
  common question; refuse to answer when no approved source matches.
- **Customer Context** — safely read authorized customer information for the
  authenticated customer.
- **Ticket Handling** — look up and create support tickets (read + create only).
- **Escalation Triage** — classify requests as ambiguous / unsupported / sensitive /
  high-risk and prepare an escalation with context.
- **Approval Protocol** — propose a sensitive action, request human approval, and
  respect the decision.

## 9. Tools Required

Each tool MUST have clear boundaries, permissions, inputs, outputs, and failure
handling (constitution Principle 5):

- **Knowledge retrieval tool** — search/retrieve approved knowledge; read-only.
- **Customer info tool** — read authorized customer information; read-only,
  scoped to the authenticated customer.
- **Ticket lookup tool** — read ticket information; read-only.
- **Ticket creation tool** — create a new support ticket; write, but cannot modify
  existing tickets.
- **Escalation tool** — route a case to the human support queue with context.
- **Approval request tool** — submit a sensitive action for human approval and
  receive the decision.

## 10. MCP Requirements (justification)

MCP integration is **justified** for this feature because the Worker must discover
and call approved tools and skills through a **bounded, permissioned, contract-driven
interface**. MCP servers provide the standardized surface through which the Worker
can:

- Discover available tools/skills and their declared inputs/outputs.
- Enforce tool boundaries and permissions (least privilege).
- Return structured, machine-parseable results and explicit failure handling.

The concrete set of MCP servers and how they map to the tools in Section 9 is a
**planning decision**, not a specification decision. The spec-level requirement is
that every tool be exposed through a bounded, permissioned integration layer with
declared contracts; MCP is the preferred mechanism to satisfy that requirement.

## 11. Data Requirements

- **Approved support knowledge** — the source of truth the Worker answers from;
  maintained by administrators; read-only to the Worker.
- **Customer account data** — limited profile information used to serve authorized
  requests; access MUST be scoped and authorized.
- **Support ticket data** — ticket records the Worker may read and create.
- **Conversation / transcript data** — the chat session content, retained for
  context, evaluation, and audit.
- **Escalation and approval records** — which cases were escalated/approved, by
  whom, with what decision.
- **Worker action log** — every action, decision, and data access for traceability.

Data requirements MUST follow data minimization, defined retention, and access
control. Specific storage and retention are Plan-phase decisions.

## 12. Human Approval and Escalation Requirements

- Escalation MUST occur when the request is ambiguous, unsupported, sensitive, or
  high-risk, or when the Worker lacks authorization to act.
- An escalation MUST include sufficient context for a human to act: conversation
  summary, reason for escalation, and relevant authorized data.
- Sensitive or irreversible actions MUST require human approval before execution.
- The Worker MUST wait for the approval decision and MUST NOT act while pending.
- Approved actions proceed; denied actions MUST NOT proceed, and the customer is
  informed appropriately.
- Escalation and approval decisions MUST be recorded for audit.

## 13. Security and Authorization Requirements

- **Least privilege**: the Worker may access only the data and tools required for
  the current authorized action.
- **Authorization before access**: the Worker MUST verify authorization before
  retrieving or acting on any customer or ticket data.
- **Session scoping**: for customer data, access is scoped to the authenticated
  customer.
- **Role-based limits**: the Worker's permitted actions are bounded by its role
  (e.g., create + read tickets, never update/close/delete).
- **No secrets**: secrets MUST never be hardcoded or committed; they MUST be
  provided via environment/vault mechanisms (Plan concern).
- **Audit**: all data access and actions MUST be logged for audit.

## 14. Safety and Governance Requirements

- The Worker MUST NOT fabricate information or overpromise outcomes.
- The Worker MUST NOT take irreversible or high-impact actions without human
  approval.
- The Worker MUST stay within its defined authorization boundary at all times.
- The Worker MUST be deterministic where possible and evaluated against measurable
  criteria before and after changes.
- Governance decisions (data handling, autonomy limits, escalation rules) MUST be
  documented and reviewed.

## 15. Evaluation Requirements

Evaluation MUST be defined alongside the outcome and applied continuously
(constitution Principle 6):

- A **golden/eval set** of representative customer requests with expected outcomes
  (correct answer, correct escalation, correct refusal, correct approval flow).
- **Graders** that verify correctness, appropriateness, escalation accuracy, and
  refusal behavior.
- A **containment metric** measuring how many requests the Worker resolves without
  a human.
- Evaluations MUST be recorded for every implemented change; tests MUST be written
  and shown to fail before implementation.

## 16. Success Metrics

Measurable, technology-agnostic outcomes:

- **SC-001**: At least 70% of in-scope, low-risk requests are resolved by the
  Worker without human intervention (containment rate).
- **SC-002**: At least 90% of the Worker's answers drawn from approved knowledge
  are factually correct as judged by a human reviewer.
- **SC-003**: 0% of answers are fabricated (the Worker never invents a fact, price,
  or policy).
- **SC-004**: Escalation precision — the Worker escalates the correct cases; it
  does not under-escalate sensitive/high-risk requests, and over-escalation is
  below 20% of in-scope cases.
- **SC-005**: The Worker never accesses or returns another customer's data.
- **SC-006**: Sensitive/irreversible actions are never executed without human
  approval (100% gated).
- **SC-007**: Customers receive a reply to a chat message within ~15 seconds (p95).

## 17. Failure Cases

- **Wrong answer**: the Worker returns an incorrect answer drawn from approved
  knowledge (knowledge error or mis-application).
- **Fabricated answer**: the Worker invents an answer not in approved knowledge
  (MUST NOT happen; SC-003).
- **Authorization breach**: the Worker accesses or returns another customer's data
  (MUST NOT happen; SC-005).
- **Under-escalation**: the Worker fails to escalate a sensitive/high-risk request.
- **Over-escalation**: the Worker escalates cases that should be resolved
  automatically, reducing containment.
- **Unauthorized action**: the Worker takes an action beyond its role (e.g.,
  updating/closing a ticket).
- **Tool failure**: a tool is unavailable or returns an error; the Worker MUST fail
  safely and not guess.
- **Misunderstanding**: the Worker misclassifies intent and responds off-target.

## 18. Edge Cases

- Customer is not authenticated or authorization cannot be verified.
- Request references another customer's data.
- No match in approved knowledge for the question.
- Ticket lookup or creation fails (system unavailable, validation error).
- Multiple intents in a single message.
- Empty, extremely long, or unsupported-language messages.
- Abusive or out-of-scope requests.
- Duplicate ticket creation attempts.
- The customer follows up with an unrelated question mid-session.

## 19. Out of Scope

For this first feature, the following are explicitly **out of scope**:

- Resolving sensitive, high-risk, or irreversible issues autonomously (refunds,
  payments, account changes, data deletion, legal/compliance matters) — these
  always require a human.
- Updating, closing, or deleting existing tickets.
- Phone / voice channel.
- Multi-language support beyond a single default language.
- Proactive/outbound messaging or marketing.
- Learning from live interactions or training on customer data without approval.
- Deep integrations with arbitrary third-party systems beyond the listed tools.

## 20. Acceptance Criteria

The feature is accepted when all of the following hold:

1. A customer asking a common, low-risk question covered by approved knowledge
   receives a correct, approved answer (US1).
2. When no approved answer exists, the Worker does not fabricate one and instead
   says it cannot answer and/or escalates (US1, SC-003).
3. An authenticated customer's request about their own account/ticket returns
   accurate authorized info; requests for another customer's data are refused
   (US2, SC-005).
4. A valid issue leads to a new ticket with a confirmation reference; the Worker
   cannot modify existing tickets (US3).
5. Ambiguous, unsupported, sensitive, or high-risk requests are escalated to a
   human with context, not answered directly (US4).
6. Sensitive/irreversible actions are gated behind human approval and never
   executed without it (US5, SC-006).
7. Every action and decision is logged and traceable (NFR-007).
8. All success metrics in Section 16 are met or have a documented measurement path.
9. Evaluations (Section 15) exist and pass before implementation is considered
   complete.

---

## Assumptions

- The customer is authenticated by the host platform before any personal data
  access is attempted.
- An approved support knowledge base exists and is maintained by administrators;
  it is the only source of truth for answers.
- Human support agents and administrators are available to review escalations and
  approvals.
- "Low-risk" means the request has no financial, irreversible, or high-impact
  consequence.
- The default channel is interactive chat messaging.
- Authorization uses a hybrid model: session scoping for the customer plus
  role-based limits on the Worker's permitted actions.

## Unresolved Decisions

The following are intentionally deferred to the Plan phase and must not block
specification approval:

- The exact set of common questions / scope of the initial approved knowledge
  base.
- The concrete mapping of tools (Section 9) to MCP servers and their deployment.
- Channel/UX details for presenting escalations and approvals to humans.
- Data retention periods and storage mechanisms.
