import { describe, expect, it } from "vitest";
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, readdirSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  generateOption,
  generateAndSavePredictions,
  loadLatestPredictions,
  type PredictionSet,
} from "./predictions-loader";
import type { Draw } from "../../lib/lotto/score";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REAL_RULES_PATH = path.resolve(__dirname, "../../../../RULES.md");
const REAL_RULES_2_PATH = path.resolve(__dirname, "../../../../RULES_2.md");

function makeDraws(count: number): Draw[] {
  const draws: Draw[] = [];
  for (let i = 1; i <= count; i++) {
    const numbers = Array.from({ length: 6 }, (_, j) => ((i + j) % 45) + 1).sort((a, b) => a - b);
    draws.push({ drwNo: i, numbers, date: `2020-01-${String((i % 28) + 1).padStart(2, "0")}` });
  }
  return draws;
}

describe("generateOption", () => {
  it("returns null when rules path does not exist", () => {
    const result = generateOption(path.join(tmpdir(), "does-not-exist-rules.md"), makeDraws(10));
    expect(result).toBeNull();
  });

  it("returns predictions with correct count when rules path exists", () => {
    const draws = makeDraws(30);
    const result = generateOption(REAL_RULES_PATH, draws);
    expect(result).not.toBeNull();
    expect(Array.isArray(result!.predictions)).toBe(true);
    expect(result!.predictions.length).toBeGreaterThan(0);
    for (const combo of result!.predictions) {
      expect(combo).toHaveLength(6);
    }
  });
});

describe("generateAndSavePredictions", () => {
  function tempDir(): string {
    return mkdtempSync(path.join(tmpdir(), "predictions-test-"));
  }

  it("throws when the primary rules path does not exist", () => {
    const draws = makeDraws(10);
    const outputDir = tempDir();
    expect(() =>
      generateAndSavePredictions(draws, {
        rulesPath: path.join(tmpdir(), "missing-rules.md"),
        rules2Path: REAL_RULES_2_PATH,
        outputDir,
      }),
    ).toThrow();
  });

  it("writes a file to a temp outputDir with correct path pattern and content shape", () => {
    const draws = makeDraws(30);
    const outputDir = tempDir();
    const result = generateAndSavePredictions(draws, {
      rulesPath: REAL_RULES_PATH,
      rules2Path: REAL_RULES_2_PATH,
      outputDir,
    });

    expect(result.based_on_drwNo).toBe(30);
    expect(result.option1.predictions.length).toBeGreaterThan(0);
    expect(typeof result.generated_at).toBe("string");
    expect(result.generated_at).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+09:00$/);

    const roundDir = path.join(outputDir, "round_31");
    const files = readdirSync(roundDir) as string[];
    expect(files.length).toBe(1);
    expect(files[0]).toMatch(/^predictions_31_\d{8}_\d{6}\.json$/);

    const written = JSON.parse(readFileSync(path.join(roundDir, files[0]), "utf-8")) as PredictionSet;
    expect(written.based_on_drwNo).toBe(30);
    expect(written.option1.predictions.length).toBeGreaterThan(0);
  });

  it("sets option2 to null when rules2Path does not exist", () => {
    const draws = makeDraws(30);
    const outputDir = tempDir();
    const result = generateAndSavePredictions(draws, {
      rulesPath: REAL_RULES_PATH,
      rules2Path: path.join(tmpdir(), "missing-rules-2.md"),
      outputDir,
    });
    expect(result.option2).toBeNull();
  });
});

describe("loadLatestPredictions", () => {
  function tempDir(): string {
    return mkdtempSync(path.join(tmpdir(), "predictions-load-test-"));
  }

  function writeFixture(dir: string, roundName: string, fileName: string, data: PredictionSet) {
    const roundDir = path.join(dir, roundName);
    mkdirSync(roundDir, { recursive: true });
    writeFileSync(path.join(roundDir, fileName), JSON.stringify(data), "utf-8");
  }

  it("returns null for an empty temp directory", () => {
    const dir = tempDir();
    expect(loadLatestPredictions(dir)).toBeNull();
  });

  it("picks the file with the latest generated_at, not the one alphabetically first", () => {
    const dir = tempDir();

    // "a_older" sorts before "z_newer" alphabetically, but z_newer has the later generated_at.
    const older: PredictionSet = {
      based_on_drwNo: 100,
      generated_at: "2026-01-01T00:00:00+09:00",
      option1: { predictions: [[1, 2, 3, 4, 5, 6]] },
      option2: null,
    };
    const newer: PredictionSet = {
      based_on_drwNo: 101,
      generated_at: "2026-06-01T00:00:00+09:00",
      option1: { predictions: [[7, 8, 9, 10, 11, 12]] },
      option2: null,
    };

    // Both in the same round dir; the alphabetically-FIRST filename holds the NEWER data,
    // proving selection is driven by generated_at, not filename order.
    writeFixture(dir, "round_101", "predictions_101_aaa_newer.json", newer);
    writeFixture(dir, "round_101", "predictions_101_zzz_older.json", older);

    const result = loadLatestPredictions(dir);
    expect(result).not.toBeNull();
    expect(result!.data.generated_at).toBe(newer.generated_at);
    expect(result!.data.based_on_drwNo).toBe(101);
  });

  it("picks the latest generated_at across different round directories, not by zero-padding-free round-number sort", () => {
    const dir = tempDir();

    // Reproduces the exact bug predict.py's comment warns about: "predictions_1_..." sorts
    // alphabetically AFTER "predictions_1242_..." because "9" > "1" as a string, even though
    // round 1242 is chronologically much later. round_9 here holds the newer generated_at.
    const olderRound1242: PredictionSet = {
      based_on_drwNo: 1241,
      generated_at: "2020-01-01T00:00:00+09:00",
      option1: { predictions: [[1, 2, 3, 4, 5, 6]] },
      option2: null,
    };
    const newerRound9: PredictionSet = {
      based_on_drwNo: 8,
      generated_at: "2026-06-01T00:00:00+09:00",
      option1: { predictions: [[7, 8, 9, 10, 11, 12]] },
      option2: null,
    };

    writeFixture(dir, "round_1242", "predictions_1242_20200101_000000.json", olderRound1242);
    writeFixture(dir, "round_9", "predictions_9_20260601_000000.json", newerRound9);

    const result = loadLatestPredictions(dir);
    expect(result).not.toBeNull();
    expect(result!.data.generated_at).toBe(newerRound9.generated_at);
    expect(result!.data.based_on_drwNo).toBe(8);
  });
});
