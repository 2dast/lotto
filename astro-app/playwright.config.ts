import { defineConfig } from "@playwright/test";

// 빌드하지 않고 이미 만들어진 dist/를 astro preview로 서빙한다.
// astro build는 동행복권 API를 호출하므로 E2E가 직접 빌드하지 않는다 (CI는 빌드 스텝 뒤에 실행).
// vitest가 수집하지 않도록 파일명은 *.e2e.ts로 둔다.
export default defineConfig({
  testDir: "e2e",
  testMatch: "**/*.e2e.ts",
  reporter: "list",
  use: {
    baseURL: "http://localhost:4321/lotto/",
    colorScheme: "light",
  },
  projects: [{ name: "chromium", use: { browserName: "chromium" } }],
  webServer: {
    command: "npm run preview -- --port 4321 --ignore-lock",
    url: "http://localhost:4321/lotto/",
    reuseExistingServer: !process.env.CI,
  },
});
