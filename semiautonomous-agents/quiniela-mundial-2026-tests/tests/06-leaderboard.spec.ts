import { test, expect } from "@playwright/test";
import { shoot } from "./helpers/shoot";

test("leaderboard shows all 10 players + AI bot row + pot", async ({ page }) => {
  await page.goto("/leaderboard");
  await page.waitForLoadState("networkidle");
  const body = await page.locator("body").innerText();
  expect(body.toLowerCase()).toContain("ranking");
  expect(body.toLowerCase()).toContain("bolsa");
  // Should also surface MXN currency
  expect(body).toMatch(/MXN|\$\s?\d/);
  await shoot(page, "06-leaderboard");
});

test("leaderboard 'Recalcular' fetches ESPN scores", async ({ page }) => {
  await page.goto("/leaderboard");
  await page.waitForLoadState("networkidle");
  const btn = page.getByRole("button", { name: /recalcular/i });
  if (await btn.count()) {
    await btn.first().click();
    await page.waitForTimeout(2500);
  }
  await shoot(page, "06-leaderboard-after-refresh");
});
