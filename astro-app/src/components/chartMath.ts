// Pure helpers ported from scripts/report_template.html's <script> block.
// Kept framework-agnostic (no DOM) so they can run at Astro build time and be
// unit-tested directly with vitest.

export function odd(combo: number[]): number {
  return combo.filter((n) => n % 2 === 1).length;
}

export function maxConsecutive(combo: number[]): number {
  const s = [...combo].sort((a, b) => a - b);
  let maxRun = 1;
  let curRun = 1;
  for (let i = 1; i < s.length; i++) {
    curRun = s[i] === s[i - 1] + 1 ? curRun + 1 : 1;
    maxRun = Math.max(maxRun, curRun);
  }
  return maxRun;
}

export function zoneCount(combo: number[], lo: number, hi: number): number {
  return combo.filter((n) => n >= lo && n <= hi).length;
}

// 동행복권 공식 번호 구간 색상: 1-10 노랑, 11-20 파랑, 21-30 빨강, 31-40 회색, 41-45 초록
export function officialColor(n: number): string {
  if (n <= 10) return "#fbc400";
  if (n <= 20) return "#69c8f2";
  if (n <= 30) return "#ff7272";
  if (n <= 40) return "#aaaaaa";
  return "#b0d840";
}

export const ZONE_RANGES: readonly [number, number][] = [
  [1, 9],
  [10, 19],
  [20, 29],
  [30, 39],
  [40, 45],
];

export const SET_COLOR_VARS = [
  "--set-1",
  "--set-2",
  "--set-3",
  "--set-4",
  "--set-5",
  "--set-6",
  "--set-7",
  "--set-8",
];

/**
 * 같은 값을 가진 세트가 여러 개면 점을 살짝 세로로 벌려서 겹치지 않게 한다.
 * Returns, for each prediction index (in input order), the vertical offset
 * index `j` and the total number of points sharing that value — mirrors the
 * `byValue` grouping in the original renderRangeCharts().
 */
export function groupOverlappingPoints(values: number[]): { offsetIndex: number; groupSize: number }[] {
  const byValue = new Map<number, number[]>();
  values.forEach((v, i) => {
    const list = byValue.get(v) ?? [];
    list.push(i);
    byValue.set(v, list);
  });

  const result: { offsetIndex: number; groupSize: number }[] = new Array(values.length);
  for (const idxs of byValue.values()) {
    idxs.forEach((setIdx, j) => {
      result[setIdx] = { offsetIndex: j, groupSize: idxs.length };
    });
  }
  return result;
}
