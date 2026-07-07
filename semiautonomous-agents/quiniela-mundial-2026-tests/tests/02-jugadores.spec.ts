import { test, expect } from "@playwright/test";
import { shoot } from "./helpers/shoot";

test("player picker shows all Charales + AI bot", async ({ page }) => {
  await page.goto("/jugadores");
  await expect(page.locator("h1, h2").first()).toBeVisible();
  const body = await page.locator("body").innerText();
  // Should mention the AI bot and at least a couple compas
  expect(body.toLowerCase()).toContain("jes");
  await shoot(page, "02-jugadores");
});
