import { existsSync, mkdirSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { loadRules } from "../../lib/lotto/rules";
import { scoreNumbers, type Draw } from "../../lib/lotto/score";
import { generatePredictions } from "../../lib/lotto/generate";

export interface PredictionOption {
  predictions: number[][];
}

export interface PredictionSet {
  based_on_drwNo: number;
  generated_at: string;
  option1: PredictionOption;
  option2: PredictionOption | null;
}

export function generateOption(rulesPath: string, draws: Draw[]): PredictionOption | null {
  if (!existsSync(rulesPath)) {
    return null;
  }
  const rules = loadRules(rulesPath);
  const scores = scoreNumbers(draws, rules);
  return { predictions: generatePredictions(rules, scores) };
}

export interface GenerateAndSaveOptions {
  rulesPath: string;
  rules2Path: string;
  outputDir: string;
}

export function generateAndSavePredictions(draws: Draw[], options: GenerateAndSaveOptions): PredictionSet {
  const { rulesPath, rules2Path, outputDir } = options;

  const option1 = generateOption(rulesPath, draws);
  if (option1 === null) {
    throw new Error(`${rulesPath} 파일이 없습니다`);
  }
  const option2 = generateOption(rules2Path, draws);

  const lastDrwNo = draws.reduce((max, d) => Math.max(max, d.drwNo), 0);

  const now = new Date();
  const kst = new Date(now.getTime() + 9 * 60 * 60 * 1000);
  const pad = (n: number) => String(n).padStart(2, "0");
  const year = kst.getUTCFullYear();
  const month = pad(kst.getUTCMonth() + 1);
  const day = pad(kst.getUTCDate());
  const hour = pad(kst.getUTCHours());
  const minute = pad(kst.getUTCMinutes());
  const second = pad(kst.getUTCSeconds());
  const generatedAt = `${year}-${month}-${day}T${hour}:${minute}:${second}+09:00`;
  const stamp = `${year}${month}${day}_${hour}${minute}${second}`;

  const output: PredictionSet = {
    based_on_drwNo: lastDrwNo,
    generated_at: generatedAt,
    option1,
    option2,
  };

  const nextDraw = lastDrwNo + 1;
  const roundDir = path.join(outputDir, `round_${nextDraw}`);
  mkdirSync(roundDir, { recursive: true });
  const outputPath = path.join(roundDir, `predictions_${nextDraw}_${stamp}.json`);
  writeFileSync(outputPath, JSON.stringify(output, null, 2), "utf-8");

  return output;
}

export function listAllPredictions(
  predictionsDir: string,
): { filename: string; data: PredictionSet }[] {
  if (!existsSync(predictionsDir)) {
    return [];
  }

  const candidates: { filename: string; data: PredictionSet }[] = [];
  for (const roundEntry of readdirSync(predictionsDir, { withFileTypes: true })) {
    if (!roundEntry.isDirectory() || !roundEntry.name.startsWith("round_")) continue;
    const roundDir = path.join(predictionsDir, roundEntry.name);
    for (const fileEntry of readdirSync(roundDir, { withFileTypes: true })) {
      if (!fileEntry.isFile()) continue;
      if (!fileEntry.name.startsWith("predictions_") || !fileEntry.name.endsWith(".json")) continue;
      const filePath = path.join(roundDir, fileEntry.name);
      const data = JSON.parse(readFileSync(filePath, "utf-8")) as PredictionSet;
      candidates.push({ filename: fileEntry.name, data });
    }
  }
  return candidates;
}

export function loadLatestPredictions(
  predictionsDir: string,
): { filename: string; data: PredictionSet } | null {
  const candidates = listAllPredictions(predictionsDir);
  if (candidates.length === 0) return null;

  return candidates.reduce((latest, current) =>
    current.data.generated_at > latest.data.generated_at ? current : latest,
  );
}
