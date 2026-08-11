import { defineConfig, devices } from "@playwright/test";

/**
 * E2E smoke tests for the AI Support Worker UI (T060).
 *
 * These exercise the real Next.js frontend against the running FastAPI backend
 * and Postgres. They are author-and-run via the quickstart (T063): start
 * docker-compose (backend + frontend), then run `npx playwright test`.
 *
 * Servers:
 *   frontend  http://localhost:3000
 *   backend   http://localhost:8000
 */
export default defineConfig({
  testDir: "./e2e",
  timeout: 30_000,
  fullyParallel: false,
  retries: 1,
  reporter: [["list"]],
  globalSetup: "./e2e/global-setup",

  use: {
    baseURL: "http://localhost:3000",
    trace: "on-first-retry",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  // No webServer: the quickstart (docker compose up) is expected to have the
  // backend (:8000) and frontend (:3000) already running when these run.
});