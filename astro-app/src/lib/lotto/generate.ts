import { passesFilters } from "./filters";
import type { PatternFilters, Rules } from "./rules";
import { ALL_NUMBERS } from "./score";

export function weightedSample(candidates: number[], scores: Record<number, number>, k: number): number[] {
  const pool = [...candidates];
  const picked: number[] = [];
  for (let i = 0; i < k; i++) {
    const weights = pool.map((n) => scores[n] + 0.01);
    const totalWeight = weights.reduce((a, b) => a + b, 0);
    let r = Math.random() * totalWeight;
    let chosenIndex = pool.length - 1;
    for (let j = 0; j < weights.length; j++) {
      r -= weights[j];
      if (r <= 0) {
        chosenIndex = j;
        break;
      }
    }
    const chosen = pool[chosenIndex];
    picked.push(chosen);
    pool.splice(chosenIndex, 1);
  }
  return picked;
}

export function generateCombo(
  pool: number[],
  scores: Record<number, number>,
  filters: PatternFilters,
  exclude: Set<number>,
  include: Set<number>,
  maxAttempts = 2000,
): number[] | null {
  const candidates = pool.filter((n) => !exclude.has(n));
  for (let i = 0; i < maxAttempts; i++) {
    const combo = new Set(include);
    const remaining = candidates.filter((n) => !combo.has(n));
    for (const n of weightedSample(remaining, scores, 6 - combo.size)) {
      combo.add(n);
    }
    const sorted = [...combo].sort((a, b) => a - b);
    if (passesFilters(sorted, filters)) {
      return sorted;
    }
  }
  return null;
}

export function generatePredictions(rules: Rules, scores: Record<number, number>): number[][] {
  const filters = rules.pattern_filters;
  const exclude = new Set(rules.exclude_numbers ?? []);
  const include = new Set(rules.include_numbers ?? []);
  const numPredictions = rules.num_predictions;

  const pool = ALL_NUMBERS.filter((n) => !exclude.has(n));

  const predictions: number[][] = [];
  const seen = new Set<string>();
  let attempts = 0;
  while (predictions.length < numPredictions && attempts < numPredictions * 500) {
    attempts += 1;
    const combo = generateCombo(pool, scores, filters, exclude, include);
    if (combo === null) continue;
    const key = combo.join(",");
    if (seen.has(key)) continue;
    seen.add(key);
    predictions.push(combo);
  }
  return predictions;
}
