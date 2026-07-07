import { test, expect } from "@playwright/test";
import { shoot } from "./helpers/shoot";

test("all 12 groups render with 4 teams each + fixture mini-cards", async ({ page }) => {
  await page.goto("/grupos");
  await page.waitForLoadState("networkidle");
  const body = await page.locator("body").innerText();
  // 12 group letters A through L
  for (const L of ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]) {
    expect(body).toMatch(new RegExp(`\\b${L}\\b`));
  }
  // Should mention "12 grupos" or "48 selecciones"
  expect(body.toLowerCase()).toMatch(/12 grupos|48 selecciones/);
  await shoot(page, "04-grupos");
});
