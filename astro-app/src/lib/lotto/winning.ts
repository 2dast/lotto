// 추첨이 끝난 회차의 당첨번호를 예측 세트와 견주는 순수 함수들.
// 상세 리포트(reports/[round]/[file].astro)의 "당첨 결과 분석" 섹션이 쓴다.

import { odd, maxConsecutive, zoneCount } from "../../components/chartMath";

export interface ConditionRange {
  label: string;
  allowedMin: number;
  allowedMax: number;
}

export interface ConditionResult extends ConditionRange {
  value: number;
  pass: boolean;
}

const sum = (combo: number[]): number => combo.reduce((a, b) => a + b, 0);
const zone = (lo: number, hi: number) => (combo: number[]): number => zoneCount(combo, lo, hi);

// 조건 라벨 → 번호 조합에서 그 값을 뽑는 함수. 라벨은 리포트의 조건 비교 표와 같은 문자열이다.
const METRICS: Record<string, (combo: number[]) => number> = {
  "합계": sum,
  "홀수 개수": odd,
  "최대 연속": maxConsecutive,
  "1-9구간 개수": zone(1, 9),
  "10-19구간 개수": zone(10, 19),
  "20-29구간 개수": zone(20, 29),
  "30-39구간 개수": zone(30, 39),
  "40-45구간 개수": zone(40, 45),
  "1-31 구간 개수": zone(1, 31),
  "32-45 구간 개수": zone(32, 45),
};

export function metricValue(label: string, combo: number[]): number {
  const fn = METRICS[label];
  if (!fn) throw new Error(`알 수 없는 조건 라벨: ${label}`);
  return fn(combo);
}

// 세트가 당첨번호 6개와 겹치는 개수. 보너스 번호는 세지 않는다 (대시보드와 같은 기준).
export function countHits(combo: number[], winning: number[]): number {
  const w = new Set(winning);
  return combo.filter((n) => w.has(n)).length;
}

// 번호 조합이 안의 허용 범위(양끝 포함)를 조건별로 통과하는지 판정한다.
export function evaluateConditions(combo: number[], conditions: ConditionRange[]): ConditionResult[] {
  return conditions.map((c) => {
    const value = metricValue(c.label, combo);
    return { ...c, value, pass: value >= c.allowedMin && value <= c.allowedMax };
  });
}

// 세트들의 조건 값 평균. 세트가 없으면 null.
export function averageMetric(label: string, sets: number[][]): number | null {
  if (sets.length === 0) return null;
  return sets.reduce((acc, combo) => acc + metricValue(label, combo), 0) / sets.length;
}
