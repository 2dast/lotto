// data/draws.json의 최신 회차가 추첨 시각 기준 기대 회차보다 뒤처졌는지 검사한다.
// draws-loader는 API 실패 시 기존 데이터로 폴백하므로 빌드 자체는 성공한다.
// 이 검사가 그 "조용한 실패"를 워크플로 실패로 드러낸다.
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const DRAWS_PATH = path.join(ROOT, "data", "draws.json");

// 기준점: 1241회차 추첨 = 2026-09-12(토) 20:35 KST. 이후 매주 토요일 20:35 KST 추첨.
const ANCHOR_DRW_NO = 1241;
const ANCHOR_DRAW_MS = Date.parse("2026-09-12T20:35:00+09:00");
const WEEK_MS = 7 * 24 * 60 * 60 * 1000;

export function expectedLatestDrawNo(now = new Date()) {
  const weeks = Math.floor((now.getTime() - ANCHOR_DRAW_MS) / WEEK_MS);
  return ANCHOR_DRW_NO + Math.max(0, weeks);
}

export function latestDrawNo(draws) {
  return draws.reduce((max, d) => Math.max(max, d.drwNo), 0);
}

if (import.meta.url === pathToFileURL(path.resolve(process.argv[1] ?? "")).href) {
  const latest = latestDrawNo(JSON.parse(readFileSync(DRAWS_PATH, "utf-8")));
  const expected = expectedLatestDrawNo();
  if (latest < expected) {
    console.error(
      `::error::최신 회차 ${latest}가 기대 회차 ${expected}보다 뒤처졌습니다. 수집 로그(동행복권 API 요청 실패 여부)를 확인하세요.`,
    );
    process.exit(1);
  }
  console.log(`최신 회차 ${latest} (기대 ${expected}) — OK`);
}
