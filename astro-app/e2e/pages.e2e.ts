import { test, expect, type Page } from "@playwright/test";

const MOBILE = { width: 390, height: 844 };
const DESKTOP = { width: 1280, height: 800 };

async function expectNoHorizontalScroll(page: Page) {
  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
  );
  expect(overflow).toBeLessThanOrEqual(0);
}

// 리포트 경로는 매주 바뀌므로 사이드바 링크에서 읽는다.
async function firstReportPath(page: Page): Promise<string> {
  await page.goto("reports/");
  const src = await page.locator(".draw-body a").first().getAttribute("data-src");
  expect(src).toBeTruthy();
  return src as string;
}

const drawerPages = [
  { name: "대시보드", path: "", themeBtn: "#theme-btn", mobileThemeBtn: "#theme-btn" },
  { name: "리포트 목록", path: "reports/", themeBtn: "#theme-btn-desktop", mobileThemeBtn: "#theme-btn-mobile" },
];

for (const p of drawerPages) {
  test.describe(`${p.name} 모바일 드로어`, () => {
    test.use({ viewport: MOBILE });

    test("닫힌 드로어는 inert이고 aria-expanded가 false다", async ({ page }) => {
      await page.goto(p.path);
      await expect(page.locator("#menu-btn")).toHaveAttribute("aria-expanded", "false");
      expect(await page.locator("#sidebar").evaluate((el: HTMLElement) => el.inert)).toBe(true);
    });

    test("햄버거로 열면 aria-expanded가 true이고 inert가 풀린다", async ({ page }) => {
      await page.goto(p.path);
      await page.locator("#menu-btn").click();
      await expect(page.locator("#menu-btn")).toHaveAttribute("aria-expanded", "true");
      await expect(page.locator("#sidebar")).toHaveClass(/is-open/);
      expect(await page.locator("#sidebar").evaluate((el: HTMLElement) => el.inert)).toBe(false);
    });

    test("Esc로 닫으면 상태가 되돌아간다", async ({ page }) => {
      await page.goto(p.path);
      await page.locator("#menu-btn").click();
      await page.keyboard.press("Escape");
      await expect(page.locator("#menu-btn")).toHaveAttribute("aria-expanded", "false");
      await expect(page.locator("#sidebar")).not.toHaveClass(/is-open/);
      expect(await page.locator("#sidebar").evaluate((el: HTMLElement) => el.inert)).toBe(true);
    });

    test("배경을 누르면 닫힌다", async ({ page }) => {
      await page.goto(p.path);
      await page.locator("#menu-btn").click();
      await page.locator("#sidebar-backdrop").click({ position: { x: 360, y: 400 } });
      await expect(page.locator("#menu-btn")).toHaveAttribute("aria-expanded", "false");
    });

    test("가로 스크롤이 없다", async ({ page }) => {
      await page.goto(p.path);
      await expectNoHorizontalScroll(page);
    });

    test("테마 토글이 data-theme과 aria-label을 바꾼다", async ({ page }) => {
      await page.goto(p.path);
      const btn = page.locator(p.mobileThemeBtn);
      await expect(btn).toHaveAttribute("aria-label", "다크 모드로 전환");
      await btn.click();
      await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
      await expect(btn).toHaveAttribute("aria-label", "라이트 모드로 전환");
    });
  });

  test.describe(`${p.name} 데스크톱`, () => {
    test.use({ viewport: DESKTOP });

    test("사이드바가 항상 보이고 가로 스크롤이 없다", async ({ page }) => {
      await page.goto(p.path);
      await expect(page.locator("#sidebar")).toBeVisible();
      expect(await page.locator("#sidebar").evaluate((el: HTMLElement) => el.inert)).toBe(false);
      await expectNoHorizontalScroll(page);
    });

    test("테마 토글이 data-theme을 바꾼다", async ({ page }) => {
      await page.goto(p.path);
      await page.locator(p.themeBtn).click();
      await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
    });
  });
}

for (const viewport of [MOBILE, DESKTOP]) {
  test(`개별 리포트는 ${viewport.width}px에서 가로 스크롤이 없다`, async ({ page }) => {
    await page.setViewportSize(viewport);
    const src = await firstReportPath(page);
    await page.goto(src);
    await expectNoHorizontalScroll(page);
  });
}

// 가장 오래된 리포트의 회차는 이미 추첨됐으므로 Ⅰ·Ⅱ 표에 당첨 결과가 얹힌다.
async function oldestReportPath(page: Page): Promise<string> {
  await page.goto("reports/");
  const src = await page.locator(".draw-body a").last().getAttribute("data-src");
  expect(src).toBeTruthy();
  return src as string;
}

test.describe("개별 리포트의 당첨 결과", () => {
  test("추첨된 회차는 당첨번호 띠와 Ⅰ·Ⅱ 표의 당첨 결과를 보여준다", async ({ page }) => {
    await page.goto(await oldestReportPath(page));
    await expect(page.getByRole("group", { name: /회차 당첨번호/ }).locator(".ball")).toHaveCount(7);
    await expect(page.getByText("1등 당첨금")).toBeVisible();
    // Ⅰ 조건 비교: 당첨번호 열과 통과 수 행
    await expect(page.getByRole("columnheader", { name: "당첨번호" })).toBeVisible();
    await expect(page.getByRole("rowheader", { name: "통과 수" })).toBeVisible();
    await expect(page.getByText(/통과|미달/).first()).toBeVisible();
    // Ⅱ 추천 세트: 적중 열, 당첨 행, 평균 행
    await expect(page.getByRole("columnheader", { name: "적중" }).first()).toBeVisible();
    await expect(page.locator(".win-row").first()).toBeVisible();
    await expect(page.locator(".avg-row").first()).toBeVisible();
    // 별도 Ⅲ 섹션은 없다
    await expect(page.getByRole("heading", { name: /당첨 결과 분석/ })).toHaveCount(0);
  });

  test("최신 리포트가 추첨 전이면 안내 한 줄만 나오고 표는 그대로다", async ({ page }) => {
    await page.goto(await firstReportPath(page));
    const notDrawn = page.getByText("아직 추첨 전입니다");
    if (await notDrawn.count()) {
      await expect(page.getByText("1등 당첨금")).toHaveCount(0);
      await expect(page.getByRole("columnheader", { name: "당첨번호" })).toHaveCount(0);
      await expect(page.locator(".win-row")).toHaveCount(0);
    } else {
      await expect(page.getByText("1등 당첨금")).toBeVisible();
    }
  });

  for (const viewport of [MOBILE, DESKTOP]) {
    test(`추첨된 회차 리포트는 ${viewport.width}px에서 가로 스크롤이 없다`, async ({ page }) => {
      await page.setViewportSize(viewport);
      await page.goto(await oldestReportPath(page));
      await expectNoHorizontalScroll(page);
    });
  }
});
