// predictions/ 폴더의 최신 예측 파일을 README.md 마커 구간에 반영한다.
// scripts/update_readme.py의 TS/Node 포트.
import { readFileSync, writeFileSync, readdirSync, existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const README_PATH = path.join(ROOT, "README.md");
const PREDICTIONS_DIR = path.join(ROOT, "predictions");

const START_MARKER = "<!-- PREDICTION:START -->";
const END_MARKER = "<!-- PREDICTION:END -->";

function findLatestPredictionsFile(dirPath = PREDICTIONS_DIR) {
  if (!existsSync(dirPath)) {
    throw new Error(`${dirPath}에 round_<회차>/predictions_*.json 파일이 없습니다`);
  }

  const candidates = [];
  for (const roundEntry of readdirSync(dirPath, { withFileTypes: true })) {
    if (!roundEntry.isDirectory() || !roundEntry.name.startsWith("round_")) continue;
    const roundDir = path.join(dirPath, roundEntry.name);
    for (const fileEntry of readdirSync(roundDir, { withFileTypes: true })) {
      if (!fileEntry.isFile()) continue;
      if (!fileEntry.name.startsWith("predictions_") || !fileEntry.name.endsWith(".json")) continue;
      const filePath = path.join(roundDir, fileEntry.name);
      const data = JSON.parse(readFileSync(filePath, "utf-8"));
      candidates.push({ generatedAt: data.generated_at, path: filePath });
    }
  }

  if (candidates.length === 0) {
    throw new Error(`${dirPath}에 round_<회차>/predictions_*.json 파일이 없습니다`);
  }

  // 파일명의 회차 번호가 zero-padding 없이 들어가 이름순 정렬은 신뢰할 수 없다.
  // generated_at(ISO8601) 값으로 정렬해 진짜 최신 파일을 고른다.
  return candidates.reduce((latest, current) => (current.generatedAt > latest.generatedAt ? current : latest)).path;
}

// predict.py가 예전엔 {"predictions": [...]} 형태(1안만)로 저장했다 — 그 시절 파일도 계속 읽을 수 있게 둘 다 지원.
function option1Predictions(data) {
  if (data.option1) return data.option1.predictions;
  return data.predictions;
}

function buildBlock(data) {
  const lines = [
    START_MARKER,
    `- ${data.based_on_drwNo + 1}회차 예측`,
    `- 생성 시각: ${data.generated_at}`,
    "",
  ];
  option1Predictions(data).forEach((combo, i) => {
    lines.push(`${i + 1}. ${combo.join(", ")}`);
  });
  lines.push(END_MARKER);
  return lines.join("\n");
}

function main() {
  const latestPath = findLatestPredictionsFile();
  const data = JSON.parse(readFileSync(latestPath, "utf-8"));
  const readme = readFileSync(README_PATH, "utf-8");

  const pattern = new RegExp(
    `${START_MARKER.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}[\\s\\S]*?${END_MARKER.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}`,
  );
  if (!pattern.test(readme)) {
    throw new Error("README.md에서 PREDICTION 마커를 찾을 수 없습니다");
  }

  const updated = readme.replace(pattern, buildBlock(data));
  writeFileSync(README_PATH, updated, "utf-8");
  console.log("README.md 갱신 완료");
}

main();
