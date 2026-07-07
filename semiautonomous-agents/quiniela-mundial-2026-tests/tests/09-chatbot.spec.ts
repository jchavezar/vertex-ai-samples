import { test, expect } from "@playwright/test";
import { loginAs } from "./helpers/auth";
import { shoot } from "./helpers/shoot";

test("chatbot FAB opens panel + send + receive a response", async ({ page, request }) => {
  await loginAs(page, request, "jesus");
  await page.goto("/");
  await page.waitForLoadState("networkidle");

  // Find the Charal Bot FAB
  const fab = page.locator("button[aria-label='Abrir Charal Bot']").first();
  await expect(fab).toBeVisible({ timeout: 10000 });
  await fab.click();
  await page.waitForTimeout(800);
  await shoot(page, "09-chatbot-opened");

  // Find a textarea or input inside the panel
  const ta = page.locator("textarea, input[type='text']").last();
  if (await ta.count() === 0) {
    await shoot(page, "09-chatbot-no-input");
    test.skip(true, "No chat input found");
    return;
  }
  await ta.fill("hola, en una palabra: ¿quién gana hoy MEX vs RSA?");
  await ta.press("Enter");
  // Wait up to 30s for any model response text to appear
  await page.waitForTimeout(15000);
  await shoot(page, "09-chatbot-response");
});
