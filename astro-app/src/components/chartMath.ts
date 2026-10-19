// Pure helpers ported from scripts/report_template.html's <script> block.
// Kept framework-agnostic (no DOM) so they can run at Astro build time and be
// unit-tested directly with vitest.

import { ballZoneIndex } from "../lib/lotto/ballZone";

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
const OFFICIAL_COLORS = ["#fbc400", "#69c8f2", "#ff7272", "#aaaaaa", "#b0d840"];

export function officialColor(n: number): string {
  return OFFICIAL_COLORS[ballZoneIndex(n)];
}

export const ZONE_RANGES: readonly [number, number][] = [
  [1, 9],
  [10, 19],
  [20, 29],
  [30, 39],
  [40, 45],
];
