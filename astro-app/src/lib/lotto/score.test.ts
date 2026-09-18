import { describe, it, expect } from "vitest";
import { scoreNumbers, ALL_NUMBERS } from "./score";
import type { Draw } from "./score";
import type { Rules } from "./rules";

function makeRules(overrides: Partial<Rules["frequency"]> = {}): Rules {
  return {
    frequency: {
      all_time_weight: 0.5,
      recent_weight: 0.5,
      recent_window: 20,
      mode: "hot",
      ...overrides,
    },
    pattern_filters: {
      odd_even_ratio: [0, 6],
      max_consecutive: 6,
      sum_range: [21, 255],
      zones: [],
    },
    num_predictions: 5,
    exclude_numbers: [],
    include_numbers: [],
  };
}

function draw(drwNo: number, numbers: number[]): Draw {
  return { drwNo, numbers, date: "2024-01-01" };
}

describe("scoreNumbers", () => {
  it("blends all-time and recent frequency in hot mode", () => {
    const draws = [
      draw(1, [1, 2, 3, 4, 5, 6]),
      draw(2, [1, 2, 3, 7, 8, 9]),
      draw(3, [1, 10, 11, 12, 13, 14]),
    ];
    const rules = makeRules({ all_time_weight: 0.5, recent_weight: 0.5, recent_window: 2 });
    const scores = scoreNumbers(draws, rules);

    // all-time counts: 1->3, 2->2, 3->2, others 1 or 0
    // max_all = 3
    // recent (last 2 draws: draw2, draw3): 1->2, 2->1,3->1,7->1,8->1,9->1,10->1,11->1,12->1,13->1,14->1
    // max_recent = 2
    const allTimeNorm1 = 3 / 3;
    const recentNorm1 = 2 / 2;
    expect(scores[1]).toBeCloseTo(0.5 * allTimeNorm1 + 0.5 * recentNorm1, 10);

    const allTimeNorm2 = 2 / 3;
    const recentNorm2 = 1 / 2;
    expect(scores[2]).toBeCloseTo(0.5 * allTimeNorm2 + 0.5 * recentNorm2, 10);

    // number 45 never appears -> 0 contribution
    expect(scores[45]).toBe(0);
  });

  it("inverts normalized frequencies in cold mode", () => {
    const draws = [draw(1, [1, 2, 3, 4, 5, 6])];
    const rules = makeRules({ all_time_weight: 0.5, recent_weight: 0.5, recent_window: 1, mode: "cold" });
    const scores = scoreNumbers(draws, rules);

    // number 1 appears -> all_time_norm=1, recent_norm=1 -> inverted to 0
    expect(scores[1]).toBeCloseTo(0, 10);
    // number 45 never appears -> norm=0 -> inverted to 1
    expect(scores[45]).toBeCloseTo(1, 10);
  });

  it("handles recent_window of 0 as the whole draws array (Python draws[-0:] semantics)", () => {
    const draws = [draw(1, [1, 2, 3, 4, 5, 6]), draw(2, [7, 8, 9, 10, 11, 12])];
    const rules = makeRules({ all_time_weight: 0, recent_weight: 1, recent_window: 0 });
    const scores = scoreNumbers(draws, rules);
    // recent_window=0 -> slice(-0) === whole array -> recent counts equal all-time counts
    for (const n of [1, 7]) {
      expect(scores[n]).toBeCloseTo(1, 10);
    }
  });

  it("handles recent_window smaller than draws.length", () => {
    const draws = [draw(1, [1, 2, 3, 4, 5, 6]), draw(2, [7, 8, 9, 10, 11, 12]), draw(3, [1, 8, 20, 21, 22, 23])];
    const rules = makeRules({ all_time_weight: 0, recent_weight: 1, recent_window: 1 });
    const scores = scoreNumbers(draws, rules);
    // only last draw counted: [1,8,20,21,22,23]
    expect(scores[1]).toBeCloseTo(1, 10);
    expect(scores[7]).toBe(0);
  });

  it("handles recent_window larger than draws.length (uses all draws)", () => {
    const draws = [draw(1, [1, 2, 3, 4, 5, 6]), draw(2, [7, 8, 9, 10, 11, 12])];
    const rules = makeRules({ all_time_weight: 0, recent_weight: 1, recent_window: 1000 });
    const scores = scoreNumbers(draws, rules);
    expect(scores[1]).toBeCloseTo(1, 10);
    expect(scores[7]).toBeCloseTo(1, 10);
  });

  it("returns a score for all 45 numbers with no NaN when draws is empty", () => {
    const rules = makeRules();
    const scores = scoreNumbers([], rules);
    expect(Object.keys(scores).length).toBe(45);
    for (const n of ALL_NUMBERS) {
      expect(Number.isNaN(scores[n])).toBe(false);
      expect(scores[n]).toBe(0);
    }
  });
});
