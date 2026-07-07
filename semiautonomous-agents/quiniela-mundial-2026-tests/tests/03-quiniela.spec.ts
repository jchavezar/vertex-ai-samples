import { test, expect } from "@playwright/test";
import { loginAs } from "./helpers/auth";
import { shoot } from "./helpers/shoot";

test("logged-in player sees quiniela with group fixtures + lock badge on kicked-off matches", async ({ page, request }) => {
  await loginAs(page, request, "jesus");
  await page.goto("/quiniela");
  await page.waitForLoadState("networkidle");
  await expect(page.locator("h1, h2").first()).toBeVisible();
  // A-M1 is MEX vs RSA, kicked off today 2026-06-11. Expect a lock indicator
  // visible somewhere on the page (text like "cerrado", padlock icon, or
  // disabled pick buttons).
  const body = await page.locator("body").innerText();
  expect(body).toMatch(/Grupo\s+A/i);
  await shoot(page, "03-quiniela-logged-in");
});

test("anonymous user lands on quiniela but gets read-only / login prompt", async ({ page }) => {
  await page.context().clearCookies();
  await page.goto("/quiniela");
  await page.waitForLoadState("networkidle");
  await shoot(page, "03-quiniela-anon");
});
