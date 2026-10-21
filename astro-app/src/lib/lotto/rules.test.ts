import path from "node:path";
import { describe, expect, it } from "vitest";
import { loadRules, parseRuleLines, RULES_PATH } from "./rules";

describe("loadRules", () => {
  it("parses RULES.md with expected fields", () => {
    const rules = loadRules();
    expect(rules.pattern_filters.odd_even_ratio).toEqual([1, 5]);
    expect(rules.pattern_filters.sum_range).toEqual([88, 189]);
    expect(rules.pattern_filters.max_consecutive).toBe(3);
    expect(rules.pattern_filters.zones).toEqual([
      { range: [1, 9], min: 0, max: 3 },
      { range: [10, 19], min: 0, max: 3 },
      { range: [20, 29], min: 0, max: 3 },
      { range: [30, 39], min: 0, max: 3 },
      { range: [40, 45], min: 1, max: 2 },
    ]);
    expect(rules.num_predictions).toBe(5);
    expect(rules.frequency.all_time_weight).toBe(0.4);
    expect(rules.frequency.recent_weight).toBe(0.6);
    expect(rules.frequency.recent_window).toBe(20);
    expect(rules.frequency.mode).toBe("hot");
    expect(rules.exclude_numbers).toEqual([]);
    expect(rules.include_numbers).toEqual([]);
  });

  it("parses RULES_2.md with expected fields", () => {
    const rules2Path = path.resolve(path.dirname(RULES_PATH), "RULES_2.md");
    const rules2 = loadRules(rules2Path);
    expect(rules2.frequency.mode).toBe("cold");
    expect(rules2.pattern_filters.zones).toContainEqual({ range: [1, 9], min: 1, max: 3 });
    expect(rules2.pattern_filters.zones).toContainEqual({ range: [40, 45], min: 0, max: 0 });
  });

  it("throws on unknown keyword", () => {
    expect(() => parseRuleLines(["not_a_real_keyword 1 2"])).toThrow();
  });
});

describe("parseRuleLines validation", () => {
  it("throws when a numeric value is missing or not a number", () => {
    expect(() => parseRuleLines(["sum 88"])).toThrow(/sum/);
    expect(() => parseRuleLines(["odd_even a b"])).toThrow(/odd_even/);
    expect(() => parseRuleLines(["freq_all_weight abc"])).toThrow(/freq_all_weight/);
  });

  it("throws when a range has min greater than max", () => {
    expect(() => parseRuleLines(["sum 189 88"])).toThrow(/sum/);
    expect(() => parseRuleLines(["zone 1 9 min 3 max 1"])).toThrow(/zone/);
  });

  it("throws when include has more than 6 numbers", () => {
    expect(() => parseRuleLines(["include 1 2 3 4 5 6 7"])).toThrow(/include/);
  });

  it("throws when include/exclude numbers are outside 1-45", () => {
    expect(() => parseRuleLines(["include 46"])).toThrow(/include/);
    expect(() => parseRuleLines(["exclude 0"])).toThrow(/exclude/);
  });

  it("throws when the same number is in both include and exclude", () => {
    expect(() => parseRuleLines(["include 7", "exclude 7"])).toThrow(/7/);
  });

  it("throws when exclude leaves fewer than 6 candidates", () => {
    const nums = Array.from({ length: 40 }, (_, i) => i + 1).join(" ");
    expect(() => parseRuleLines([`exclude ${nums}`])).toThrow(/exclude/);
  });

  it("throws when freq_recent_window is less than 1", () => {
    expect(() => parseRuleLines(["freq_recent_window 0"])).toThrow(/freq_recent_window/);
  });
});
