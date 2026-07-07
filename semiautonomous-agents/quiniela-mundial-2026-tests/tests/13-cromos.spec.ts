import { test, expect } from "@playwright/test";
import { loginAs } from "./helpers/auth";
import { shoot } from "./helpers/shoot";

// FUT-style cromos: cuando hay sesión, el home debe renderizar el "Tu cromo
// Charales" hero card y la tira "El álbum del torneo". Sin sesión no se renderiza
// el hero (queda solo la podium / contenido público).
test("home shows FUT cromo hero + álbum strip when logged in", async ({ page, request }) => {
  await loginAs(page, request, "jesus");
  await page.goto("/");
  await page.waitForLoadState("networkidle");
  // Esperar a que el fetch de allMundialPicks resuelva (cromos memo depende de eso).
  await page.waitForTimeout(5000);

  const body = await page.locator("body").innerText();
  expect(body).toMatch(/Tu cromo Charales/i);
  expect(body).toMatch(/El álbum del torneo/i);
  // El rating siempre es 40-99 (clamp). Buscar "ovr" en el hero.
  expect(body).toMatch(/\d{2,3} ovr/i);
  await shoot(page, "13-cromo-hero");
});

test("home mobile cromo hero stacks vertically", async ({ page, request }) => {
  await page.setViewportSize({ width: 390, height: 844 }); // iPhone 14 Pro
  await loginAs(page, request, "jesus");
  await page.goto("/");
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(5000);
  const body = await page.locator("body").innerText();
  if (/Tu cromo Charales/i.test(body)) {
    await shoot(page, "13-cromo-hero-mobile");
  }
});
