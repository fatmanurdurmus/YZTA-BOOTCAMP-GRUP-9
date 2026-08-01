import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  timeout: 30_000,
  fullyParallel: true,
  reporter: "list",
  use: {
    baseURL: "http://localhost:5173",
    trace: "on-first-retry",
  },
  webServer: {
    command: "npm run dev",
    url: "http://localhost:5173",
    reuseExistingServer: true, // Açık olan sunucuyu doğrudan kullanmasını zorunlu kıldık
    timeout: 120 * 1000, // Zaman aşımını 120 saniyeye çıkardık
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});