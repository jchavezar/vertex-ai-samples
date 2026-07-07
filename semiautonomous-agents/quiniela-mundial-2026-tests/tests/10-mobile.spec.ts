import { test, expect } from "@playwright/test";
import { shoot } from "./helpers/shoot";

test("mobile: home renders without layout breakage", async ({ page }) => {
  await page.goto("/");
  await page.waitForLoadState("networkidle");
  await expect(page.locator("h1").first()).toBeVisible();
  await shoot(page, "10-mobile-home");
});

test("mobile: grupos page", async ({ page }) => {
  await page.goto("/grupos");
  await page.waitForLoadState("networkidle");
  await shoot(page, "10-mobile-grupos");
});

test("mobile: partidos live tab", async ({ page }) => {
  await page.goto("/partidos");
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(2000);
  await shoot(page, "10-mobile-partidos");
});

test("mobile: leaderboard", async ({ page }) => {
  await page.goto("/leaderboard");
  await page.waitForLoadState("networkidle");
  await shoot(page, "10-mobile-leaderboard");
});
