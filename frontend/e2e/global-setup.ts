import { Client } from "pg";

/**
 * Reset worker state before the e2e run so the smoke tests are deterministic.
 *
 * The backend (and the golden eval) persist escalations/approvals/conversations
 * to the same Postgres, so assertions like "No open escalations." would
 * otherwise be poisoned by items left over from earlier runs. Truncating the
 * state tables here gives each `npm run e2e` a clean slate.
 *
 * Credentials default to the compose/`.env.example` dev values and can be
 * overridden with E2E_DB_* vars.
 */
export default async function globalSetup(): Promise<void> {
  const client = new Client({
    host: process.env.E2E_DB_HOST || "localhost",
    port: Number(process.env.E2E_DB_PORT || 5432),
    user: process.env.E2E_DB_USER || "support",
    password: process.env.E2E_DB_PASSWORD || "support",
    database: process.env.E2E_DB_NAME || "support",
  });

  await client.connect();
  try {
    await client.query(`
      TRUNCATE TABLE escalations, approval_requests, conversations,
        conversation_messages, worker_action_log
        RESTART IDENTITY CASCADE;
    `);
  } finally {
    await client.end();
  }
}
