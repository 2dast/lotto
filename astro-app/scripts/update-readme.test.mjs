import { describe, it, expect } from "vitest";
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { replacePredictionBlock, findLatestPredictionsFile } from "./update-readme.mjs";

const START = "<!-- PREDICTION:START -->";
const END = "<!-- PREDICTION:END -->";

const data = {
  based_on_drwNo: 1246,
  generated_at: "2026-10-19T22:39:32+09:00",
  option1: { predictions: [[1, 2, 3, 4, 5, 6], [7, 8, 9, 10, 11, 12]] },
};

describe("replacePredictionBlock", () => {
  it("replaces only the marker section", () => {
    const readme = `# head\n${START}\nold\n${END}\n\nfooter\n`;
    const out = replacePredictionBlock(readme, data);
    expect(out.startsWith("# head\n")).toBe(true);
    expect(out.endsWith("\n\nfooter\n")).toBe(true);
    expect(out).toContain("- 1247회차 예측");
    expect(out).toContain("1. 1, 2, 3, 4, 5, 6");
    expect(out).not.toContain("old");
  });

  it("throws when the markers are missing", () => {
    expect(() => replacePredictionBlock("# no markers\n", data)).toThrow("마커");
  });

  it("is idempotent", () => {
    const once = replacePredictionBlock(`${START}\nold\n${END}\n`, data);
    expect(replacePredictionBlock(once, data)).toBe(once);
  });

  it("reads the legacy {predictions: [...]} format", () => {
    const legacy = { based_on_drwNo: 1, generated_at: "x", predictions: [[1, 2, 3, 4, 5, 6]] };
    expect(replacePredictionBlock(`${START}\n${END}`, legacy)).toContain("1. 1, 2, 3, 4, 5, 6");
  });
});

describe("findLatestPredictionsFile", () => {
  it("picks the file with the latest generated_at, not the latest name", () => {
    const dir = mkdtempSync(path.join(tmpdir(), "readme-"));
    try {
      for (const [round, at] of [["round_999", "2026-10-20T00:00:00+09:00"], ["round_1000", "2026-10-10T00:00:00+09:00"]]) {
        mkdirSync(path.join(dir, round));
        writeFileSync(path.join(dir, round, "predictions_x.json"), JSON.stringify({ generated_at: at }));
      }
      expect(findLatestPredictionsFile(dir)).toContain("round_999");
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });

  it("throws when there are no prediction files", () => {
    const dir = mkdtempSync(path.join(tmpdir(), "readme-"));
    try {
      expect(() => findLatestPredictionsFile(dir)).toThrow("predictions");
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });
});
