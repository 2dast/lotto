import { describe, it, expect } from "vitest";
import { countHits, evaluateConditions, averageMetric, metricValue } from "./winning";
import type { ConditionRange } from "./winning";

describe("countHits", () => {
  const winning = [16, 22, 23, 24, 27, 28];

  it("겹치는 번호가 없으면 0", () => {
    expect(countHits([1, 2, 3, 4, 5, 6], winning)).toBe(0);
  });

  it("일부만 겹치면 그 개수", () => {
    expect(countHits([1, 16, 23, 30, 40, 45], winning)).toBe(2);
  });

  it("전부 같으면 6", () => {
    expect(countHits([28, 27, 24, 23, 22, 16], winning)).toBe(6);
  });

  it("보너스 번호는 당첨번호 배열에 없으므로 세지 않는다", () => {
    expect(countHits([6, 1, 2, 3, 4, 5], winning)).toBe(0);
  });
});

describe("metricValue", () => {
  const combo = [16, 22, 23, 24, 27, 28];

  it("합계·홀수·최대 연속", () => {
    expect(metricValue("합계", combo)).toBe(140);
    expect(metricValue("홀수 개수", combo)).toBe(2);
    expect(metricValue("최대 연속", combo)).toBe(3);
  });

  it("5구간과 1-31/32-45 구간 개수", () => {
    expect(metricValue("10-19구간 개수", combo)).toBe(1);
    expect(metricValue("20-29구간 개수", combo)).toBe(5);
    expect(metricValue("40-45구간 개수", combo)).toBe(0);
    expect(metricValue("1-31 구간 개수", combo)).toBe(6);
    expect(metricValue("32-45 구간 개수", combo)).toBe(0);
  });

  it("모르는 라벨은 에러", () => {
    expect(() => metricValue("없는 조건", combo)).toThrow();
  });
});

describe("evaluateConditions", () => {
  const conditions: ConditionRange[] = [
    { label: "합계", allowedMin: 88, allowedMax: 189 },
    { label: "최대 연속", allowedMin: 1, allowedMax: 2 },
    { label: "40-45구간 개수", allowedMin: 0, allowedMax: 0 },
  ];

  it("허용 범위 양끝 값은 통과", () => {
    // 합계가 허용 범위 하한(88)과 정확히 같은 조합
    const combo = [1, 5, 10, 17, 25, 30];
    expect(combo.reduce((a, b) => a + b, 0)).toBe(88);
    const [sumResult] = evaluateConditions(combo, conditions);
    expect(sumResult.value).toBe(88);
    expect(sumResult.pass).toBe(true);
  });

  it("범위를 벗어나면 미달", () => {
    const results = evaluateConditions([16, 22, 23, 24, 27, 28], conditions);
    expect(results.map((r) => r.pass)).toEqual([true, false, true]);
  });

  it("40-45구간이 0~0인 안은 41이 하나라도 있으면 미달", () => {
    const results = evaluateConditions([3, 12, 21, 30, 38, 41], conditions);
    expect(results[2].value).toBe(1);
    expect(results[2].pass).toBe(false);
  });
});

describe("averageMetric", () => {
  it("세트가 없으면 null", () => {
    expect(averageMetric("합계", [])).toBeNull();
  });

  it("세트들의 평균", () => {
    const sets = [
      [1, 2, 3, 4, 5, 6], // 합계 21
      [10, 11, 12, 13, 14, 15], // 합계 75
    ];
    expect(averageMetric("합계", sets)).toBe(48);
    expect(averageMetric("최대 연속", sets)).toBe(6);
  });
});
