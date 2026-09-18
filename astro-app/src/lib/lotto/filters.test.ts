import { describe, expect, it } from "vitest";
import { loadRules } from "./rules";
import { passesFilters } from "./filters";

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
