import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
export const RULES_PATH = path.resolve(__dirname, "../../../../RULES.md");

export interface Zone {
  range: [number, number];
  min: number;
  max: number;
}

export interface PatternFilters {
  odd_even_ratio: [number, number];
  max_consecutive: number;
  sum_range: [number, number];
  zones: Zone[];
}

export interface Frequency {
  all_time_weight: number;
  recent_weight: number;
  recent_window: number;
  mode: "hot" | "cold";
}

export interface Rules {
  frequency: Frequency;
  pattern_filters: PatternFilters;
  num_predictions: number;
  exclude_numbers: number[];
  include_numbers: number[];
}

function toInt(token: string | undefined, keyword: string): number {
  const n = Number(token);
  if (token === undefined || !Number.isInteger(n)) {
    throw new Error(`${keyword}: 정수 값이 필요합니다 ('${token ?? ""}')`);
  }
  return n;
}

function toNumber(token: string | undefined, keyword: string): number {
  const n = Number(token);
  if (token === undefined || !Number.isFinite(n)) {
    throw new Error(`${keyword}: 숫자 값이 필요합니다 ('${token ?? ""}')`);
  }
  return n;
}

function toRange(lo: number, hi: number, keyword: string): [number, number] {
  if (lo > hi) {
    throw new Error(`${keyword}: 최소(${lo})가 최대(${hi})보다 클 수 없습니다`);
  }
  return [lo, hi];
}

function toBallNumbers(tokens: string[], keyword: string): number[] {
  return tokens.map((t) => {
    const n = toInt(t, keyword);
    if (n < 1 || n > 45) {
      throw new Error(`${keyword}: 번호는 1~45여야 합니다 (${n})`);
    }
    return n;
  });
}

export function parseRuleLines(lines: string[]): Rules {
  const zones: Zone[] = [];
  const rules: Rules = {
    frequency: { all_time_weight: 0.5, recent_weight: 0.5, recent_window: 20, mode: "hot" },
    pattern_filters: {
      odd_even_ratio: [0, 6],
      max_consecutive: 6,
      sum_range: [21, 255],
      zones: [],
    },
    num_predictions: 5,
    exclude_numbers: [],
    include_numbers: [],
  };

  for (const rawLine of lines) {
    const line = rawLine.split("#", 1)[0].trim();
    if (!line) continue;
    const tokens = line.split(/\s+/);
    const keyword = tokens[0];

    switch (keyword) {
      case "odd_even":
        rules.pattern_filters.odd_even_ratio = toRange(toInt(tokens[1], keyword), toInt(tokens[2], keyword), keyword);
        break;
      case "sum":
        rules.pattern_filters.sum_range = toRange(toInt(tokens[1], keyword), toInt(tokens[2], keyword), keyword);
        break;
      case "consecutive_max":
        rules.pattern_filters.max_consecutive = toInt(tokens[1], keyword);
        break;
      case "zone": {
        const [min, max] = toRange(toInt(tokens[4], keyword), toInt(tokens[6], keyword), keyword);
        zones.push({
          range: toRange(toInt(tokens[1], keyword), toInt(tokens[2], keyword), keyword),
          min,
          max,
        });
        break;
      }
      case "predictions":
        rules.num_predictions = toInt(tokens[1], keyword);
        break;
      case "freq_all_weight":
        rules.frequency.all_time_weight = toNumber(tokens[1], keyword);
        break;
      case "freq_recent_weight":
        rules.frequency.recent_weight = toNumber(tokens[1], keyword);
        break;
      case "freq_recent_window": {
        const window = toInt(tokens[1], keyword);
        if (window < 1) {
          throw new Error(`${keyword}: 1 이상이어야 합니다 (${window})`);
        }
        rules.frequency.recent_window = window;
        break;
      }
      case "freq_mode":
        if (tokens[1] !== "hot" && tokens[1] !== "cold") {
          throw new Error(`freq_mode는 hot/cold만 허용: '${tokens[1]}'`);
        }
        rules.frequency.mode = tokens[1];
        break;
      case "exclude":
        rules.exclude_numbers.push(...toBallNumbers(tokens.slice(1), keyword));
        break;
      case "include":
        rules.include_numbers.push(...toBallNumbers(tokens.slice(1), keyword));
        break;
      default:
        throw new Error(`알 수 없는 조건 키워드: '${keyword}' (줄: '${rawLine}')`);
    }
  }

  if (zones.length) {
    rules.pattern_filters.zones = zones;
  }

  const include = new Set(rules.include_numbers);
  const exclude = new Set(rules.exclude_numbers);
  if (include.size > 6) {
    throw new Error(`include: 6개를 넘을 수 없습니다 (${include.size}개)`);
  }
  const overlap = [...include].filter((n) => exclude.has(n));
  if (overlap.length > 0) {
    throw new Error(`include와 exclude에 같은 번호가 있습니다: ${overlap.join(", ")}`);
  }
  if (45 - exclude.size < 6) {
    throw new Error(`exclude: 제외 후 남는 번호가 6개 미만입니다 (${45 - exclude.size}개)`);
  }
  return rules;
}

export function loadRules(filePath: string = RULES_PATH): Rules {
  const text = readFileSync(filePath, "utf-8");
  const match = text.match(/```\r?\n([\s\S]*?)```/);
  if (!match) {
    throw new Error("RULES.md에서 조건 코드블록을 찾을 수 없습니다");
  }
  return parseRuleLines(match[1].split(/\r?\n/));
}
