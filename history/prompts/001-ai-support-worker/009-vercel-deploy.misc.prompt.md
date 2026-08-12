---
id: 009
title: Vercel deploy monorepo routing
stage: misc
date: 2026-08-12
surface: agent
model: oc/deepseek-v4-flash-free
feature: ai-support-worker
branch: main
user: Sarah Sohail
command: vercel --prod
labels: ["vercel", "deploy", "devops", "routing", "nextjs", "fastapi"]
links:
  spec: specs/001-ai-support-worker/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - vercel.json (rewritten with version 2 builds/routes; committed eac9ef2)
 - .gitignore (".vercel" appended by `vercel link`; kept)
 - backend/src/main.py (deployed as λ 35.73MB)
 - frontend/src (deployed as Next.js λ functions)
tests:
 - curl / -> 200 OK (frontend)
 - curl /api/health -> 302 to vercel.com/sso-api (Vercel SSO Protection intercepts; backend not reachable publicly)
 - vercel inspect -> Deployment Ready, both λ functions present
---

## Prompt

Please create a 'vercel.json' file at the repository root with the following configuration to handle monorepo routing between Next.js frontend and FastAPI backend:

{
  "version": 2,
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/next"
    },
    {
      "src": "backend/src/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "backend/src/main.py"
    },
    {
      "src": "/(.*)",
      "dest": "frontend/$1"
    }
  ]
}

After creating and committing 'vercel.json', please run 'vercel' to trigger the setup and production deployment. Ensure environment variables like DATABASE_URL and NEXT_PUBLIC_BACKEND_URL are set up if prompted.

## Response snapshot

Overwrote the pre-existing simple `rewrites`-only `vercel.json` with the requested
`version: 2` `builds`/`routes` config (frontend via `@vercel/next`, backend via
`@vercel/python`) and committed as `eac9ef2`.

Ran `vercel --prod --yes`. The CLI auto-linked / created the project
`sohail-nawazs-projects/ai-fde-lab` and connected the GitHub repo
`Sohail-AI-Architect/ai-customer-support-worker`. Production deployment
`dpl_ChjC7BD6PsCaqNdgabTgwfuDjeRw` finished **Ready** in ~54s with both
serverless functions present (`λ backend/src/main.py` 35.73MB + Next.js frontend
functions). Aliases: `ai-fde-lab.vercel.app`.

The frontend returns HTTP 200. `NEXT_PUBLIC_BACKEND_URL` is not referenced
anywhere in the frontend (it uses relative `/api/...` paths), and
`DATABASE_URL` in `.env` is a template placeholder with no real value.

## Outcome

- ✅ Impact: Legacy vs2 monorepo routing is live on Vercel; both Next.js and
  FastAPI are built as functions in a single project.
- 🧪 Tests: `GET /` -> 200; `GET /api/health` -> 302 to `vercel.com/sso-api`
  (Vercel SSO Protection enabled at the deployment/team level intercepts public
  API access before it reaches the Python function); `vercel inspect` confirms
  Ready with both builds.
- 📁 Files: `vercel.json` (rewritten + committed eac9ef2); `.vercel/` (gitignored);
  `.gitignore` gained a `.vercel` entry from `vercel link`.
- 🔁 Next prompts: user must (a) disable/whitelist Vercel SSO Protection in the
  dashboard to make `/api/*` publicly reachable, and (b) provide real values for
  `DATABASE_URL` (and optionally set project env vars) since the CLI deploy did
  not prompt for env vars.
- 🧠 Reflection: Deployment succeeded even though Vercel printed a warning that
  `builds` overrides Project Settings. SSO Protection is an external platform
  setting that cannot be toggled via CLI; surfacing it is the correct non-blocking
  report.

## Evaluation notes (flywheel)

- Failure modes observed: Vercel SSO Protection intercepting `/api/*` (302 to
  `vercel.com/sso-api`); env vars absent from the project (no prompted setup in
  non-interactive mode); `vercel` auto-created a `.gitignore` entry.
- Graders run and results (PASS/FAIL): PASS — deployment Ready, both λ functions
  present, frontend 200, config committed.
- Prompt variant (if applicable): n/a.
- Next experiment (smallest change to try): disable SSO Protection, set project
  env vars, redeploy, and re-test `/api/health` against `ai-fde-lab.vercel.app`.