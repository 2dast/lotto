import { describe, it, expect } from "vitest";
import { odd, maxConsecutive, zoneCount, officialColor, groupOverlappingPoints } from "./chartMath";

describe("odd", () => {
  it("counts odd numbers in a combo", () => {
    expect(odd([3, 12, 19, 24, 33, 41])).toBe(4);
  });
  it("returns 0 when all even", () => {
    expect(odd([2, 4, 6, 8, 10, 12])).toBe(0);
  });
});

describe("maxConsecutive", () => {
  it("finds the longest consecutive run regardless of input order", () => {
    expect(maxConsecutive([5, 14, 21, 28, 32, 44])).toBe(1);
    expect(maxConsecutive([1, 2, 3, 10, 20, 30])).toBe(3);
    expect(maxConsecutive([30, 3, 2, 1, 20, 10])).toBe(3);
  });
  it("returns 1 for a single-element combo", () => {
    expect(maxConsecutive([7])).toBe(1);
  });
});

describe("zoneCount", () => {
  it("counts numbers within an inclusive range", () => {
    expect(zoneCount([3, 12, 19, 24, 33, 41], 1, 9)).toBe(1);
    expect(zoneCount([3, 12, 19, 24, 33, 41], 10, 19)).toBe(2);
    expect(zoneCount([3, 12, 19, 24, 33, 41], 40, 45)).toBe(1);
  });
});

describe("officialColor", () => {
  it("maps boundaries to the official 동행복권 zone colors", () => {
    expect(officialColor(1)).toBe("#fbc400");
    expect(officialColor(10)).toBe("#fbc400");
    expect(officialColor(11)).toBe("#69c8f2");
    expect(officialColor(20)).toBe("#69c8f2");
    expect(officialColor(21)).toBe("#ff7272");
    expect(officialColor(30)).toBe("#ff7272");
    expect(officialColor(31)).toBe("#aaaaaa");
    expect(officialColor(40)).toBe("#aaaaaa");
    expect(officialColor(41)).toBe("#b0d840");
    expect(officialColor(45)).toBe("#b0d840");
  });
});

describe("groupOverlappingPoints", () => {
  it("assigns offset 0 / groupSize 1 when all values are distinct", () => {
    expect(groupOverlappingPoints([1, 2, 3])).toEqual([
      { offsetIndex: 0, groupSize: 1 },
      { offsetIndex: 0, groupSize: 1 },
      { offsetIndex: 0, groupSize: 1 },
    ]);
  });

  it("spreads duplicate values across offsets in encounter order", () => {
    expect(groupOverlappingPoints([5, 5, 3, 5])).toEqual([
      { offsetIndex: 0, groupSize: 3 },
      { offsetIndex: 1, groupSize: 3 },
      { offsetIndex: 0, groupSize: 1 },
      { offsetIndex: 2, groupSize: 3 },
    ]);
  });
});
