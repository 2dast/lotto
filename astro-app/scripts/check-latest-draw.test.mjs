import { describe, it, expect } from "vitest";
import { expectedLatestDrawNo, latestDrawNo } from "./check-latest-draw.mjs";

describe("expectedLatestDrawNo", () => {
  it("is 1241 at the anchor week before the Saturday draw", () => {
    expect(expectedLatestDrawNo(new Date("2026-09-12T20:00:00+09:00"))).toBe(1241);
  });

  it("increments exactly at the Saturday 20:35 KST draw time", () => {
    expect(expectedLatestDrawNo(new Date("2026-09-12T20:35:00+09:00"))).toBe(1241);
    expect(expectedLatestDrawNo(new Date("2026-09-19T20:34:59+09:00"))).toBe(1241);
    expect(expectedLatestDrawNo(new Date("2026-09-19T20:35:00+09:00"))).toBe(1242);
  });

  it("returns 1246 on Sunday 2026-10-18 00:28 KST (after the 10/17 draw)", () => {
    expect(expectedLatestDrawNo(new Date("2026-10-18T00:28:00+09:00"))).toBe(1246);
  });

  it("does not go below 1241 for dates before the anchor", () => {
    expect(expectedLatestDrawNo(new Date("2026-01-01T00:00:00+09:00"))).toBe(1241);
  });
});

describe("latestDrawNo", () => {
  it("returns the max drwNo regardless of order", () => {
    expect(latestDrawNo([{ drwNo: 1244 }, { drwNo: 1246 }, { drwNo: 1245 }])).toBe(1246);
  });

  it("returns 0 for an empty list", () => {
    expect(latestDrawNo([])).toBe(0);
  });
});
