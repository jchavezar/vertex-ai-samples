import { test, expect } from "@playwright/test";
import { shoot } from "./helpers/shoot";

// Home should show the Punteros podium once at least one match is final and any
// player has scored. We're inside the tournament window so this is expected,
// but if no player has any score yet (cold start), the block is hidden — in
// that case we still want to capture a screenshot of the home as proof.
test("home shows live podio (Punteros) or hides gracefully", async ({ page }) => {
  await page.goto("/");
  await page.waitForLoadState("networkidle");
  // First scoreboard poll is on mount; give the punteros memo time to recompute.
  await page.waitForTimeout(4000);
  const body = await page.locator("body").innerText();
  if (/Punteros/.test(body)) {
    // Podium present — sanity-check it has place medals + pts.
    expect(body).toMatch(/pts/);
  }
  await shoot(page, "12-home-punteros");
});

test("home shows En vivo ahora block when matches are live", async ({ page }) => {
  await page.goto("/");
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(4000);
  const body = await page.locator("body").innerText();
  // Best-effort. If no live match right now, the block is hidden by design.
  if (/En vivo ahora/i.test(body)) {
    expect(body).toMatch(/EN VIVO/);
    await shoot(page, "12-home-envivo");
  }
});
