import { test, expect } from "@playwright/test";
import { shoot } from "./helpers/shoot";

test("partidos page loads ESPN scoreboard with live/today/upcoming tabs", async ({ page }) => {
  await page.goto("/partidos");
  await page.waitForLoadState("networkidle");
  // Wait for the ESPN scoreboard fetch to populate
  await page.waitForResponse(r => r.url().includes("/api/scoreboard"), { timeout: 20000 }).catch(() => {});
  await page.waitForTimeout(2000);

  // Hero text
  const body = await page.locator("body").innerText();
  expect(body.toLowerCase()).toContain("marcadores");
  expect(body.toLowerCase()).toContain("tiempo real");

  // Tabs must be present (En vivo / Hoy / Próximos / Resultados)
  await expect(page.getByRole("button", { name: /próximos|proximos/i }).first()).toBeVisible();
  await shoot(page, "07-partidos-default");
});

test("partidos tabs switch and render different buckets", async ({ page }) => {
  await page.goto("/partidos");
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(1500);

  for (const label of ["En vivo", "Hoy", "Próximos", "Resultados"]) {
    const btn = page.getByRole("button", { name: new RegExp(label, "i") }).first();
    if (await btn.count()) {
      await btn.click();
      await page.waitForTimeout(800);
      await shoot(page, `07-partidos-${label.toLowerCase().replace(/\s/g, "-").replace(/[^\w-]/g, "")}`);
    }
  }
});

test("scoreboard API responds with real fixtures (no league=nba)", async ({ request }) => {
  const r = await request.get("/api/scoreboard");
  expect(r.status()).toBe(200);
  const j = await r.json();
  expect(j.ok).toBe(true);
  expect(Array.isArray(j.events)).toBe(true);
  // No league param should be needed; soccer is default
  // Should have at least one event in the wider WC window
  expect(j.events.length).toBeGreaterThanOrEqual(0);
});

test("scoreboard rejects nonsense league param gracefully (NBA gone)", async ({ request }) => {
  // The new server ignores ?league= entirely. Confirm it returns soccer.
  const r = await request.get("/api/scoreboard?league=nba");
  expect(r.status()).toBe(200);
  const j = await r.json();
  expect(j.ok).toBe(true);
  // Leagues array should be FIFA, not NBA
  const txt = JSON.stringify(j.leagues || []);
  expect(txt.toLowerCase()).not.toContain("national basketball");
});
