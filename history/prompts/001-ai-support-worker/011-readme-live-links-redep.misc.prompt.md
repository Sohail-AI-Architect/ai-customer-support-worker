---
id: 011
title: README live links + redeploy
stage: misc
date: 2026-08-12
surface: agent
model: oc/deepseek-v4-flash-free
feature: ai-support-worker
branch: main
user: Sarah Sohail
command: vercel --prod
labels: ["vercel", "deploy", "readme", "docs", "swagger", "github"]
links:
  spec: specs/001-ai-support-worker/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - README.md (added "🌐 Live Production (Vercel)" table; commit 47eddb9)
 - backend/src/main.py (docs_url/openapi_url -> /api/*; commit 47eddb9)
tests:
 - /chat live 200, /agent live 200, /api/docs 200 (Swagger HTML), /api/openapi.json 200 (JSON)
 - ruff src/main.py: All checks passed; app import smoke OK with docs_url=/api/docs
 - git ls-remote origin/main == local HEAD (47eddb9)
---

## Prompt

Please update README.md to include both Live Production Deployment links and Local Development instructions, then push to GitHub and redeploy on Vercel:

1. Update 'README.md' to add a prominent "🌐 Live Production (Vercel)" table right alongside the local testing routes:
   - **Live Customer Chat UI:** https://ai-fde-lab.vercel.app/chat
   - **Live Agent Dashboard:** https://ai-fde-lab.vercel.app/agent
   - **Live API Docs:** https://ai-fde-lab.vercel.app/api/docs

2. Keep the local development section ("🚀 Local Testing Routes & Setup") intact for developers running the stack via Docker.

3. Commit the updated README.md with the commit message: "docs: update README with live Vercel production deployment links".

4. Push the commit to GitHub:
   'git push origin main'

5. Trigger a fresh production rebuild and deployment on Vercel:
   'vercel --prod'

## Response snapshot

Added a `### 🌐 Live Production (Vercel)` table right after the local routes
table under the quick-access section with the three requested URLs; the
Docker/local sections were left untouched.

Smoke-tested the three links against the running production alias before
committing: `/chat` and `/agent` returned 200, but `/api/docs` returned
FastAPI's 404 — Swagger was served at `/docs` (shadowed by the frontend
catch-all). Fixed by configuring `docs_url="/api/docs"` and
`openapi_url="/api/openapi.json"` on the FastAPI app so the documented link
really works. Committed README + main.py together with the exact requested
message `47eddb9`, pushed to `origin/main` (da511d7..47eddb9), and redeployed
`vercel --prod` -> Ready in 1m.

## Outcome

- ✅ Impact: README now surfaces live production URLs; Swagger is publicly
  reachable at /api/docs; the commit is on GitHub and the production alias
  serves the new build.
- 🧪 Tests: /chat 200, /agent 200, /api/docs 200, /api/openapi.json 200;
  ruff clean; app import smoke OK; remote head matches local commit.
- 📁 Files: README.md (live table), backend/src/main.py (docs/openapi paths).
- 🔁 Next prompts: none blocking. If the frontend catch-all ever intercepts
  `/api/*`, re-check the routes order in vercel.json.
- 🧠 Reflection: The requested URL was validated rather than assumed; exposing
  Swagger required aligning FastAPI's built-in routes with the /api namespace.

## Evaluation notes (flywheel)

- Failure modes observed: /api/docs 404 (FastAPI docs not at /api/docs);
  corrected via docs_url config instead of a manual route.
- Graders run and results (PASS/FAIL): PASS — links verified, push verified,
  deployment Ready.
- Prompt variant (if applicable): n/a.
- Next experiment (smallest change to try): none needed.