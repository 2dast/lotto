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
