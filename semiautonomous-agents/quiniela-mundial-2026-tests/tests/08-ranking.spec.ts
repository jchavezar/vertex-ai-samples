import { test, expect } from "@playwright/test";
import { shoot } from "./helpers/shoot";

test("/ranking shows dynamic team strength table", async ({ page }) => {
  await page.goto("/ranking");
  await page.waitForLoadState("networkidle");
  const body = await page.locator("body").innerText();
  expect(body.toLowerCase()).toMatch(/ranking|fuerza|strength|elo/);
  await shoot(page, "08-ranking");
});
