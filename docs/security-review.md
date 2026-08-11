# Security Hardening Review (T061)

**Feature:** 001-ai-support-worker · **Branch:** `001-ai-support-worker`
**Date:** 2026-08-11 · **Status:** Pass — no hard blocks; two scoped notes.

This review verifies the standing security posture of the AI Customer Support
Worker against the constitution and spec (§ NFR-003, §13 Security and
Authorization; FR-010; SC-005; SC-006). It is a **static review** — checks
structure, secrets handling, and the exposed tool/endpoint surface. It does not
replace dynamic testing (T058/T060/T063, currently deferred pending a Postgres
dependency).

## 1. Secrets — never hardcoded or committed ✅

- `.gitignore` excludes `.env` and `.env.*` (lines 2–3). ✅
- `git ls-files` shows **no** `.env`, `.env.prod`, or env-var files tracked. ✅
- Source scan of `backend/src` and `mcp-servers` for hardcoded
  `password|secret|token|api_key = "..."` found **no** occurrences (excluding
  `os.environ`/`getenv` access and comments). ✅
- `.env.example` carries only a placeholder (`SESSION_SECRET=change-me-in-env`)
  and a default model constant; no real secrets. ✅

### Scoped note (no action required for MVP)
`DATABASE_URL` in `.env.example` is a **localhost dev credential**
(`support:support@.../support`) for the local docker-compose Postgres. This is
acceptable for local development only; it must never be reused as a production
or shared-environment password. If/when this deploys beyond localhost, provide
credentials exclusively via environment/vault (e.g. `DATABASE_URL` and
`SESSION_SECRET` injected at runtime) and keep `.env` out of any container
image and CI logs.

## 2. Least privilege — tool and API surface is bounded ✅

Full MCP tool surface exposed to the Worker (discovered across
`mcp-servers/*/src`):

| Tool | Category | Operation |
|------|----------|-----------|
| `knowledge.search` | read | read-only |
| `customer.info.get` | read | read-only, session-scoped |
| `ticket.list` | read | read-only, session-scoped |
| `ticket.get` | read | read-only, session-scoped |
| `ticket.create` | write | **create only** — no update/close/delete |
| `escalation.create` | write | hand-off to human queue (no mutate) |
| `approval.request` | write | propose-and-hold; never executes the action |

Every tool is either **read-only** or a **bounded create/propose**. There is no
update, close, or delete capability on any resource — the absence is structural,
not prompt-enforced (FR-010; ADR-002). ✅

### REST agent surface (human-operated, not Worker)
- `GET /api/agent/escalations` — read the escalation queue.
- `POST /api/agent/escalations/{id}/resolve` — resolve a handed-off case.
- `GET /api/agent/approvals` — read pending approvals.
- `POST /api/agent/approvals/{id}/decision` — approve/deny a held action.

These are agent-facing (human) endpoints, gated by agent authentication, and
are the *only* mutation path for sensitive actions — consistent with the design
that the Worker itself never executes sensitive changes (SC-006).

## 3. No update/close/delete of tickets ✅

- No `@router.put` / `@router.patch` / `@router.delete` exists in `backend/src/api`.
- No `ticket.update` / `ticket.close` / `ticket.delete` tool exists in the MCP
  surface. Requests to modify an existing ticket route to escalation
  (`escalate`, reason `ticket_modify`) and are never honored (FR-011).

## 4. Cross-customer containment (session scoping) ✅

- Every customer-data read/create and the escalation/approval tools are bound to
  the authenticated customer via `SessionScope` + `ensure_customer_scope`.
- Cross-customer reads are refused; golden cases `ticket_cross_customer` cover
  this (SC-005).

## 5. Approval gating (SC-006) ✅

- Sensitive/state-changing actions surface as the `approval` intent and are held
  as `approval_requests` in `pending` state; the Worker never executes the
  proposed action (ADR-003). Decision is recorded (`decided_by`, `decided_at`).

## Residual risks & follow-ups (≤3)

1. **Dev password reuse** — guard against promoting the localhost
   `support:support` to any non-local environment.
2. **Static triggers (cv)** — `APPROVAL_ACTIONS` and keyword escalation are
   deterministic but coarse; paraphrases can fall through (documented in
   ADR-003). A model-judged safety classifier is a future enhancement.
3. **Snapshot scope** — this review is static; dynamic E2E security assertions
   (auth bypass, injection, cross-customer API checks) land in T060 (Playwright)
   and T058 (eval), deferred until Postgres is available.

## Evidence

- `git ls-files | grep .env` → none tracked.
- Secret scan over `backend/src`, `mcp-servers` → no hardcoded credentials.
- Router scan over `backend/src/api` → no PUT/PATCH/DELETE.
- Reacting to the auth/customer-scope model: `backend/src/api/`, `backend/src/services/`.