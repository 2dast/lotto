import { describe, it, expect } from "vitest";
import { ballZoneIndex } from "./ballZone";

describe("ballZoneIndex", () => {
  it("maps each zone boundary to its zone", () => {
    expect(ballZoneIndex(1)).toBe(0);
    expect(ballZoneIndex(10)).toBe(0);
    expect(ballZoneIndex(11)).toBe(1);
    expect(ballZoneIndex(20)).toBe(1);
    expect(ballZoneIndex(21)).toBe(2);
    expect(ballZoneIndex(30)).toBe(2);
    expect(ballZoneIndex(31)).toBe(3);
    expect(ballZoneIndex(40)).toBe(3);
    expect(ballZoneIndex(41)).toBe(4);
    expect(ballZoneIndex(45)).toBe(4);
  });
  it("clamps out-of-range numbers into the first and last zone", () => {
    expect(ballZoneIndex(0)).toBe(0);
    expect(ballZoneIndex(46)).toBe(4);
  });
});
