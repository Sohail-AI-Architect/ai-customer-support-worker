import { expect, test, type Page } from "@playwright/test";

/**
 * Smoke coverage: the three core human-visible flows of the AI Support Worker.
 *
 *  1. Customer chat answers a common question from approved knowledge.
 *  2. A high-risk request escalates and appears in the agent queue for resolve.
 *  3. A sensitive action (cancel subscription) is held pending and then
 *     approved by a human agent.
 *
 * These are end-to-end: they need the backend + Postgres live (see
 * playwright.config.ts). Selectors bind to the DOM roles in ChatClient.tsx and
 * AgentClient.tsx.
 */

async function sendChat(page: Page, text: string) {
  await page.locator('input[placeholder="Type your question…"]').fill(text);
  await page.locator('button[type="submit"]').click();
  // wait for the worker reply bubble
  await page.locator(".msg.worker").last().waitFor({ timeout: 15_000 });
}

test("customer chat answers a common question from approved knowledge", async ({
  page,
}) => {
  await page.goto("/chat");
  await sendChat(page, "What is your return policy?");

  const reply = page.locator(".msg.worker").last();
  await expect(reply).toContainText(/return|days/i);
  // answer from approved knowledge: not escalated, not a created ticket
  await expect(reply.locator(".badge.escalated")).toHaveCount(0);
  await expect(reply.locator(".badge.created")).toHaveCount(0);
});

test("high-risk request escalates into the agent queue and can be resolved", async ({
  page,
}) => {
  await page.goto("/chat");
  await sendChat(page, "I want to request a refund.");
  await expect(page.locator(".msg.worker .badge.escalated")).toBeVisible();

  // the human agent sees it open in the queue and marks it resolved
  await page.goto("/agent");
  await page.getByText("No open escalations.").waitFor({ state: "detached", timeout: 15_000 }) //
    .catch(() => {}); // may already have items from other runs
  const escalateCard = page.locator(".card", { hasText: "I want to request a refund." }).first();
  await expect(escalateCard).toBeVisible({ timeout: 15_000 });
  await escalateCard.locator(".btn-resolve").click();
  await expect(page.getByText("No open escalations.")).toBeVisible({ timeout: 15_000 });
});

test("sensitive action is held pending and approved by a human agent", async ({
  page,
}) => {
  await page.goto("/chat");
  await sendChat(page, "Can you cancel my subscription?");

  // the customer is NOT given a done reply; a pending approval is created.
  const reply = page.locator(".msg.worker").last();
  await expect(reply).toContainText(/approval|human/i);

  // agent approves the pending action from the queue
  await page.goto("/agent");
  await page.getByText("No pending approvals.").waitFor({ state: "detached", timeout: 15_000 }) //
    .catch(() => {});
  const approvalCard = page
    .locator(".card", { hasText: "cancel_subscription" })
    .first();
  await expect(approvalCard).toBeVisible({ timeout: 15_000 });
  await approvalCard.locator(".btn-approve").click();
  // after approval the pending card is removed from the queue
  await expect(page.getByText("No pending approvals.")).toBeVisible({ timeout: 15_000 });
});