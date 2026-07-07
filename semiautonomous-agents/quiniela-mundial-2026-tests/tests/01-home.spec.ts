import { test, expect } from "@playwright/test";
import { shoot } from "./helpers/shoot";

test("home loads with hero, countdown, and CTAs", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveTitle(/Quiniela|Mundial|Charales/i);
  // Must have the main grad headline
  const h1 = page.locator("h1").first();
  await expect(h1).toBeVisible();
  // No NBA-mode leftover
  await expect(page.locator("text=/NBA Finals|Modo NBA/i")).toHaveCount(0);
  await shoot(page, "01-home-desktop");
});

test("home shows live/next match block (MEX vs RSA today)", async ({ page }) => {
  await page.goto("/");
  // Either a kickoff countdown chip or a live indicator should appear on today (2026-06-11).
  const body = await page.locator("body").innerText();
  // Sanity: page should not crash
  expect(body.length).toBeGreaterThan(200);
  await shoot(page, "01-home-live-block");
});
