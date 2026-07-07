import { test, expect } from "@playwright/test";
import { shoot } from "./helpers/shoot";

test("bracket page renders rounds (R32 → Final)", async ({ page }) => {
  await page.goto("/bracket");
  await page.waitForLoadState("networkidle");
  await expect(page.locator("h1, h2").first()).toBeVisible();
  const body = await page.locator("body").innerText();
  expect(body).toMatch(/Octavos|R32|Cuartos|Final/i);
  await shoot(page, "05-bracket");
});

test("bracket shows PROYECTADO state while groups are open", async ({ page }) => {
  await page.goto("/bracket");
  await page.waitForLoadState("networkidle");
  const body = await page.locator("body").innerText();
  // While no group has all 6 matches finished, every slot must read PROYECTADO,
  // and the new chip shows the count of confirmed groups out of 12.
  expect(body).toMatch(/PROYECTADO|Proyectado/);
  await expect(page.getByText(/\d+\s*\/\s*12\s+grupos\s+confirmados/i).first()).toBeVisible();
  await shoot(page, "05-bracket-proyectado");
});
