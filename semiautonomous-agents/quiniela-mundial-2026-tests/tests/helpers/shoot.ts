import { Page } from "@playwright/test";

export async function shoot(page: Page, name: string) {
  await page.waitForTimeout(800); // settle animations
  await page.screenshot({ path: `screenshots/${name}.png`, fullPage: true });
}
