import type { PatternFilters } from "./rules";

export function passesFilters(combo: number[], filters: PatternFilters): boolean {
  const oddCount = combo.filter((n) => n % 2 === 1).length;
  const [lo, hi] = filters.odd_even_ratio;
  if (!(lo <= oddCount && oddCount <= hi)) return false;

  const total = combo.reduce((a, b) => a + b, 0);
  if (!(filters.sum_range[0] <= total && total <= filters.sum_range[1])) return false;

  const sortedCombo = [...combo].sort((a, b) => a - b);
  let maxRun = 1;
  let curRun = 1;
  for (let i = 0; i < sortedCombo.length - 1; i++) {
    if (sortedCombo[i + 1] === sortedCombo[i] + 1) {
      curRun += 1;
      maxRun = Math.max(maxRun, curRun);
    } else {
      curRun = 1;
    }
  }
  if (maxRun > filters.max_consecutive) return false;

  for (const zone of filters.zones) {
    const [loZ, hiZ] = zone.range;
    const count = combo.filter((n) => loZ <= n && n <= hiZ).length;
    if (!(zone.min <= count && count <= zone.max)) return false;
  }

  return true;
}
