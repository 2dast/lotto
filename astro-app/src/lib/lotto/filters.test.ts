import { describe, expect, it } from "vitest";
import { loadRules } from "./rules";
import { passesFilters, recentNumberSet } from "./filters";

const RULES = loadRules();
const FILTERS = RULES.pattern_filters;

describe("passesFilters", () => {
  it("rejects all-even combo on odd/even ratio", () => {
    const combo = [2, 4, 6, 8, 10, 12];
    expect(passesFilters(combo, FILTERS)).toBe(false);
  });

  it("requires one to two numbers in the 40s zone", () => {
    const comboNo40s = [3, 10, 20, 21, 29, 34];
    expect(passesFilters(comboNo40s, FILTERS)).toBe(false);

    const comboTwo40s = [40, 41, 1, 10, 20, 30];
    expect(passesFilters(comboTwo40s, FILTERS)).toBe(true);

    const comboThree40s = [40, 41, 42, 1, 10, 20];
    expect(passesFilters(comboThree40s, FILTERS)).toBe(false);
  });

  it("passes a valid combo", () => {
    const combo = [3, 10, 21, 29, 34, 42];
    expect(passesFilters(combo, FILTERS)).toBe(true);
  });

  it("rejects when max consecutive run is exceeded", () => {
    const combo = [1, 12, 13, 14, 15, 30];
    expect(passesFilters(combo, FILTERS)).toBe(false);
  });

  it("rejects sum below the allowed range", () => {
    const combo = [1, 2, 3, 4, 5, 41];
    expect(passesFilters(combo, FILTERS)).toBe(false);
  });
});

describe("recent_limit", () => {
  const limited = { ...FILTERS, recent_limit: { window: 5, max: 3 } };
  const recent = new Set([3, 10, 21, 29]);

  it("allows up to max numbers from the recent set", () => {
    // 3, 10, 21 = 3개 (최대 3개 허용) — 나머지 필터는 통과하는 조합
    expect(passesFilters([3, 10, 21, 34, 42, 45], limited, recent)).toBe(true);
  });

  it("rejects a combo with more than max recent numbers", () => {
    // 3, 10, 21, 29 = 4개
    expect(passesFilters([3, 10, 21, 29, 34, 42], limited, recent)).toBe(false);
  });

  it("ignores the limit when no recent numbers are given", () => {
    expect(passesFilters([3, 10, 21, 29, 34, 42], limited)).toBe(true);
  });

  it("builds the recent set from the last N draws only", () => {
    const draws = [
      { numbers: [1, 2, 3, 4, 5, 6] },
      { numbers: [7, 8, 9, 10, 11, 12] },
      { numbers: [13, 14, 15, 16, 17, 18] },
    ];
    expect(recentNumberSet(draws, 2)).toEqual(new Set([7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]));
  });
});
