// Cookie-based session for chatbot access. HMAC-signed, 30-day expiry.
import { createHmac, timingSafeEqual } from "node:crypto";
import { cookies } from "next/headers";

const SECRET = process.env.AUTH_SECRET || "dev-secret-change-me";
const COOKIE_NAME = "q26_chat_auth";
const TTL_SECONDS = 60 * 60 * 24 * 30; // 30 days

export const DEFAULT_PIN = process.env.DEFAULT_PIN || "2026";

function sign(payload: string): string {
  return createHmac("sha256", SECRET).update(payload).digest("hex");
}

export function makeToken(playerId: string): string {
  const exp = Math.floor(Date.now() / 1000) + TTL_SECONDS;
  const payload = `${playerId}.${exp}`;
  return `${payload}.${sign(payload)}`;
}

export function verifyToken(token: string | undefined | null): { playerId: string; exp: number } | null {
  if (!token) return null;
  const parts = token.split(".");
  if (parts.length !== 3) return null;
  const [playerId, expStr, sig] = parts;
  const expected = sign(`${playerId}.${expStr}`);
  const a = Buffer.from(sig, "hex");
  const b = Buffer.from(expected, "hex");
  if (a.length !== b.length || !timingSafeEqual(a, b)) return null;
  const exp = parseInt(expStr, 10);
  if (!Number.isFinite(exp) || exp < Math.floor(Date.now() / 1000)) return null;
  return { playerId, exp };
}

export async function setAuthCookie(playerId: string): Promise<void> {
  const jar = await cookies();
  jar.set({
    name: COOKIE_NAME,
    value: makeToken(playerId),
    httpOnly: true,
    secure: true,
    sameSite: "lax",
    path: "/",
    maxAge: TTL_SECONDS,
  });
}

export async function clearAuthCookie(): Promise<void> {
  const jar = await cookies();
  jar.delete(COOKIE_NAME);
}

export async function readAuth(): Promise<{ playerId: string } | null> {
  const jar = await cookies();
  const tok = jar.get(COOKIE_NAME)?.value;
  const parsed = verifyToken(tok);
  if (parsed) return { playerId: parsed.playerId };
  // Dev-only: skip PIN login when DEV_AUTO_LOGIN names a playerId. Lets the
  // local dev server impersonate that player without setting a PIN against
  // the shared Firestore. NEVER honored in production builds.
  if (process.env.NODE_ENV !== "production" && process.env.DEV_AUTO_LOGIN) {
    return { playerId: process.env.DEV_AUTO_LOGIN };
  }
  return null;
}
