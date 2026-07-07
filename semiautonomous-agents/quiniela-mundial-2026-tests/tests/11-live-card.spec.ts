import { test, expect } from "@playwright/test";
import { loginAs } from "./helpers/auth";
import { shoot } from "./helpers/shoot";

// We're inside the tournament window (it opened 2026-06-11) so at least one
// fixture should already be in `post` (final) state and the quiniela page must
// render the new FINAL badge with score. EN VIVO is best-effort: if any match
// is in `in` state we capture it, otherwise we still validate the FINAL flow.
test("quiniela renders FINAL or EN VIVO badge for today's matches", async ({ page, request }) => {
  await loginAs(page, request, "jesus");
  await page.goto("/quiniela");
  await page.waitForLoadState("networkidle");
  // Wait one polling cycle (live-scoreboard polls every 30s; first fetch fires
  // on mount so a few seconds is enough to settle the first hydration).
  await page.waitForTimeout(3500);
  const body = await page.locator("body").innerText();
  const hasLive = /EN VIVO/.test(body);
  const hasFinal = /FINAL/.test(body);
  expect(hasLive || hasFinal, "expected a live or final badge somewhere on /quiniela").toBe(true);
  await shoot(page, "11-quiniela-live-or-final");
});
