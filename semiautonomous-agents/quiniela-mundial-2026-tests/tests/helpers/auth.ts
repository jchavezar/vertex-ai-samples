import { Page, APIRequestContext, expect } from "@playwright/test";

const ADMIN_SECRET = process.env.Q26_TEST_LOGIN_SECRET || "";

export async function loginAs(page: Page, request: APIRequestContext, playerId: string) {
  expect(ADMIN_SECRET, "Q26_TEST_LOGIN_SECRET env var required").not.toBe("");
  const res = await request.post("/api/auth/test-login", {
    headers: { "x-admin-secret": ADMIN_SECRET, "Content-Type": "application/json" },
    data: { playerId },
  });
  expect(res.status(), `test-login HTTP for ${playerId}`).toBe(200);
  // Pull the Set-Cookie from the request context and copy it into the page
  // context so subsequent page.goto sees the auth cookie.
  const cookies = await request.storageState();
  await page.context().addCookies(cookies.cookies);
  // Force the client to pick the player too (q26_player in localStorage)
  await page.addInitScript((id) => {
    try { window.localStorage.setItem("q26_player", id); } catch {}
  }, playerId);
}
