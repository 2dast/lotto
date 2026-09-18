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
        rules.pattern_filters.odd_even_ratio = [parseInt(tokens[1], 10), parseInt(tokens[2], 10)];
        break;
      case "sum":
        rules.pattern_filters.sum_range = [parseInt(tokens[1], 10), parseInt(tokens[2], 10)];
        break;
      case "consecutive_max":
        rules.pattern_filters.max_consecutive = parseInt(tokens[1], 10);
        break;
      case "zone":
        zones.push({
          range: [parseInt(tokens[1], 10), parseInt(tokens[2], 10)],
          min: parseInt(tokens[4], 10),
          max: parseInt(tokens[6], 10),
        });
        break;
      case "predictions":
        rules.num_predictions = parseInt(tokens[1], 10);
        break;
      case "freq_all_weight":
        rules.frequency.all_time_weight = parseFloat(tokens[1]);
        break;
      case "freq_recent_weight":
        rules.frequency.recent_weight = parseFloat(tokens[1]);
        break;
      case "freq_recent_window":
        rules.frequency.recent_window = parseInt(tokens[1], 10);
        break;
      case "freq_mode":
        if (tokens[1] !== "hot" && tokens[1] !== "cold") {
          throw new Error(`freq_mode는 hot/cold만 허용: '${tokens[1]}'`);
        }
        rules.frequency.mode = tokens[1];
        break;
      case "exclude":
        rules.exclude_numbers.push(...tokens.slice(1).map((t) => parseInt(t, 10)));
        break;
      case "include":
        rules.include_numbers.push(...tokens.slice(1).map((t) => parseInt(t, 10)));
        break;
      default:
        throw new Error(`알 수 없는 조건 키워드: '${keyword}' (줄: '${rawLine}')`);
    }
  }

  if (zones.length) {
    rules.pattern_filters.zones = zones;
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
