import { defineConfig, devices } from "@playwright/test";

const BASE_URL = process.env.Q26_BASE_URL || "https://quiniela-charales-2026-254356041555.us-central1.run.app";

export default defineConfig({
  testDir: "./tests",
  timeout: 60_000,
  expect: { timeout: 10_000 },
  fullyParallel: false,
  retries: 1,
  workers: 1,
  reporter: [["list"], ["html", { open: "never" }]],
  outputDir: "./test-results",
  use: {
    baseURL: BASE_URL,
    trace: "on",
    video: "on",
    screenshot: "only-on-failure",
    actionTimeout: 15_000,
    navigationTimeout: 30_000,
    viewport: { width: 1280, height: 800 },
  },
  projects: [
    {
      name: "desktop",
      use: { ...devices["Desktop Chrome"], viewport: { width: 1280, height: 800 } },
    },
    {
      name: "mobile",
      testMatch: /10-mobile\.spec\.ts/,
      use: { ...devices["Pixel 7"] },
    },
  ],
});
