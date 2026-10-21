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
  option3?: PredictionOption | null;
}

export function generateOption(rulesPath: string, draws: Draw[]): PredictionOption | null {
  if (!existsSync(rulesPath)) {
    return null;
  }
  const rules = loadRules(rulesPath);
  const scores = scoreNumbers(draws, rules);
  const predictions = generatePredictions(rules, scores);
  // 조건이 너무 엄격하면 세트가 모자라거나 비어도 조용히 저장·배포되므로 여기서 막는다.
  if (predictions.length < rules.num_predictions) {
    throw new Error(
      `${rulesPath}: 예측 ${rules.num_predictions}세트 중 ${predictions.length}세트만 생성됨 — 조건이 너무 엄격합니다`,
    );
  }
  return { predictions };
}

export interface GenerateAndSaveOptions {
  rulesPath: string;
  rules2Path: string;
  rules3Path?: string;
  outputDir: string;
  // true면 다음 회차 예측이 이미 있어도 새 파일을 추가한다 (기존 파일은 건드리지 않는다).
  force?: boolean;
}

export function generateAndSavePredictions(draws: Draw[], options: GenerateAndSaveOptions): PredictionSet {
  const { rulesPath, rules2Path, rules3Path, outputDir, force = false } = options;

  const lastDrwNo = draws.reduce((max, d) => Math.max(max, d.drwNo), 0);
  const nextDraw = lastDrwNo + 1;

  // 같은 회차는 한 번만 생성한다. 화면만 고친 push나 스케줄 재시도가 번호를 바꾸지 않게 한다.
  if (!force) {
    const existing = loadLatestForRound(outputDir, nextDraw);
    if (existing !== null) {
      console.log(`${nextDraw}회차 예측이 이미 있어 생성을 건너뜁니다 (${existing.filename})`);
      return existing.data;
    }
  }

  const option1 = generateOption(rulesPath, draws);
  if (option1 === null) {
    throw new Error(`${rulesPath} 파일이 없습니다`);
  }
  const option2 = generateOption(rules2Path, draws);
  const option3 = rules3Path ? generateOption(rules3Path, draws) : null;

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
    option3,
  };

  const roundDir = path.join(outputDir, `round_${nextDraw}`);
  mkdirSync(roundDir, { recursive: true });
  const outputPath = path.join(roundDir, `predictions_${nextDraw}_${stamp}.json`);
  writeFileSync(outputPath, JSON.stringify(output, null, 2), "utf-8");

  return output;
}

// predict.py used to save {"predictions": [...]} (option1 only, no option1/option2 wrapper)
// before the option1/option2 schema existed. Normalize those legacy files on read so every
// PredictionSet consumers see always has option1.predictions, matching the current schema.
function normalizeLegacyShape(raw: unknown): PredictionSet {
  const obj = raw as Record<string, unknown>;
  if (obj && obj.option1 === undefined && Array.isArray(obj.predictions)) {
    return {
      based_on_drwNo: obj.based_on_drwNo as number,
      generated_at: obj.generated_at as string,
      option1: { predictions: obj.predictions as number[][] },
      option2: null,
      option3: null,
    };
  }
  return raw as PredictionSet;
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
      const raw = JSON.parse(readFileSync(filePath, "utf-8"));
      candidates.push({ filename: fileEntry.name, data: normalizeLegacyShape(raw) });
    }
  }
  return candidates;
}

function loadLatestForRound(
  predictionsDir: string,
  round: number,
): { filename: string; data: PredictionSet } | null {
  const inRound = listAllPredictions(predictionsDir).filter(({ filename }) =>
    filename.startsWith(`predictions_${round}_`),
  );
  if (inRound.length === 0) return null;
  return inRound.reduce((latest, current) =>
    current.data.generated_at > latest.data.generated_at ? current : latest,
  );
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
