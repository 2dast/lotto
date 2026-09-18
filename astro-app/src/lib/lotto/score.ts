import type { Rules } from "./rules";
import type { Draw as FullDraw } from "../../content/loaders/draws-loader";

export type Draw = Pick<FullDraw, "drwNo" | "numbers" | "date">;

export const ALL_NUMBERS: number[] = Array.from({ length: 45 }, (_, i) => i + 1);

export function scoreNumbers(draws: Draw[], rules: Rules): Record<number, number> {
  const { all_time_weight: allTimeWeight, recent_weight: recentWeight, recent_window: recentWindow, mode } =
    rules.frequency;

  const allTimeCount: Record<number, number> = Object.fromEntries(ALL_NUMBERS.map((n) => [n, 0]));
  const recentCount: Record<number, number> = Object.fromEntries(ALL_NUMBERS.map((n) => [n, 0]));

  for (const drawItem of draws) {
    for (const n of drawItem.numbers) {
      allTimeCount[n] += 1;
    }
  }

  for (const drawItem of draws.slice(-recentWindow)) {
    for (const n of drawItem.numbers) {
      recentCount[n] += 1;
    }
  }

  const maxAll = Math.max(...ALL_NUMBERS.map((n) => allTimeCount[n])) || 1;
  const maxRecent = Math.max(...ALL_NUMBERS.map((n) => recentCount[n])) || 1;

  let allTimeNorm: Record<number, number> = Object.fromEntries(
    ALL_NUMBERS.map((n) => [n, allTimeCount[n] / maxAll]),
  );
  let recentNorm: Record<number, number> = Object.fromEntries(
    ALL_NUMBERS.map((n) => [n, recentCount[n] / maxRecent]),
  );

  if (mode === "cold") {
    allTimeNorm = Object.fromEntries(ALL_NUMBERS.map((n) => [n, 1 - allTimeNorm[n]]));
    recentNorm = Object.fromEntries(ALL_NUMBERS.map((n) => [n, 1 - recentNorm[n]]));
  }

  return Object.fromEntries(
    ALL_NUMBERS.map((n) => [n, allTimeWeight * allTimeNorm[n] + recentWeight * recentNorm[n]]),
  );
}
