import { describe, expect, it } from "vitest";
import { weightedSample, generateCombo, generatePredictions } from "./generate";
import { passesFilters } from "./filters";
import { ALL_NUMBERS } from "./score";
import { loadRules } from "./rules";
import type { PatternFilters, Rules } from "./rules";

const uniformScores: Record<number, number> = Object.fromEntries(ALL_NUMBERS.map((n) => [n, 1]));

describe("weightedSample", () => {
  it("returns exactly k items with no duplicates", () => {
    for (let i = 0; i < 200; i++) {
      const result = weightedSample(ALL_NUMBERS, uniformScores, 6);
      expect(result.length).toBe(6);
      expect(new Set(result).size).toBe(6);
      for (const n of result) {
        expect(ALL_NUMBERS).toContain(n);
      }
    }
  });

  it("can select every candidate when k equals candidates length", () => {
    const candidates = [1, 2, 3, 4, 5];
    const result = weightedSample(candidates, uniformScores, 5);
    expect(result.sort((a, b) => a - b)).toEqual(candidates);
  });

  it("handles zero-scored numbers (0.01 smoothing keeps them selectable)", () => {
    const scores: Record<number, number> = { 1: 0, 2: 0, 3: 0 };
    const result = weightedSample([1, 2, 3], scores, 3);
    expect(result.sort((a, b) => a - b)).toEqual([1, 2, 3]);
  });
});

const basicFilters: PatternFilters = {
  odd_even_ratio: [2, 4],
  max_consecutive: 3,
  sum_range: [100, 150],
  zones: [],
};

describe("generateCombo", () => {
  it("always returns a combo that passes filters", () => {
    for (let i = 0; i < 50; i++) {
      const combo = generateCombo(ALL_NUMBERS, uniformScores, basicFilters, new Set(), new Set());
      expect(combo).not.toBeNull();
      if (combo) {
        expect(combo.length).toBe(6);
        expect(passesFilters(combo, basicFilters)).toBe(true);
      }
    }
  });

  it("always includes forced include_numbers", () => {
    const include = new Set([10, 20]);
    for (let i = 0; i < 50; i++) {
      const combo = generateCombo(ALL_NUMBERS, uniformScores, basicFilters, new Set(), include);
      expect(combo).not.toBeNull();
      if (combo) {
        expect(combo).toContain(10);
        expect(combo).toContain(20);
      }
    }
  });

  it("never includes excluded numbers", () => {
    const exclude = new Set(ALL_NUMBERS.filter((n) => n > 30));
    const pool = ALL_NUMBERS.filter((n) => !exclude.has(n));
    for (let i = 0; i < 50; i++) {
      const combo = generateCombo(pool, uniformScores, basicFilters, exclude, new Set());
      expect(combo).not.toBeNull();
      if (combo) {
        for (const n of combo) {
          expect(exclude.has(n)).toBe(false);
        }
      }
    }
  });

  it("returns null when max_attempts is exhausted for impossible filters", () => {
    const impossible: PatternFilters = {
      odd_even_ratio: [7, 7],
      max_consecutive: 6,
      sum_range: [0, 300],
      zones: [],
    };
    const combo = generateCombo(ALL_NUMBERS, uniformScores, impossible, new Set(), new Set(), 50);
    expect(combo).toBeNull();
  });
});

describe("generatePredictions", () => {
  const rules: Rules = {
    frequency: { all_time_weight: 0.5, recent_weight: 0.5, recent_window: 20, mode: "hot" },
    pattern_filters: basicFilters,
    num_predictions: 5,
    exclude_numbers: [],
    include_numbers: [],
  };

  it("returns num_predictions distinct combos, all passing filters", () => {
    for (let trial = 0; trial < 5; trial++) {
      const predictions = generatePredictions(rules, uniformScores);
      expect(predictions.length).toBe(rules.num_predictions);
      const seen = new Set<string>();
      for (const combo of predictions) {
        expect(passesFilters(combo, basicFilters)).toBe(true);
        const key = combo.join(",");
        expect(seen.has(key)).toBe(false);
        seen.add(key);
      }
    }
  });

  it("respects exclude and include numbers", () => {
    const rulesWithConstraints: Rules = {
      ...rules,
      exclude_numbers: [1, 2, 3, 4, 5],
      include_numbers: [40, 41],
    };
    const predictions = generatePredictions(rulesWithConstraints, uniformScores);
    expect(predictions.length).toBe(rulesWithConstraints.num_predictions);
    for (const combo of predictions) {
      expect(combo).toContain(40);
      expect(combo).toContain(41);
      for (const n of [1, 2, 3, 4, 5]) {
        expect(combo).not.toContain(n);
      }
    }
  });

  it("works with real RULES.md-derived rules", () => {
    const realRules = loadRules();
    const scores: Record<number, number> = Object.fromEntries(ALL_NUMBERS.map((n) => [n, 1]));
    const predictions = generatePredictions(realRules, scores);
    expect(predictions.length).toBe(realRules.num_predictions);
    for (const combo of predictions) {
      expect(passesFilters(combo, realRules.pattern_filters)).toBe(true);
    }
  });
});
