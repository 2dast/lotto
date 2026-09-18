import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";
import { defineCollection, z } from "astro:content";
import type { Loader } from "astro/loaders";
import { loadDrawsWithUpdates, type Draw } from "./content/loaders/draws-loader";
import { generateAndSavePredictions, listAllPredictions } from "./content/loaders/predictions-loader";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
export const DRAWS_PATH = path.resolve(__dirname, "../../data/draws.json");
export const PREDICTIONS_DIR = path.resolve(__dirname, "../../predictions");
export const RULES_PATH = path.resolve(__dirname, "../../RULES.md");
export const RULES_2_PATH = path.resolve(__dirname, "../../RULES_2.md");

export function readDraws(filePath: string = DRAWS_PATH): Draw[] {
  if (!existsSync(filePath)) return [];
  return JSON.parse(readFileSync(filePath, "utf-8"));
}

export function writeDraws(draws: Draw[], filePath: string = DRAWS_PATH): void {
  writeFileSync(filePath, JSON.stringify(draws, null, 2), "utf-8");
}

// Both the draws and predictions loaders need the freshly-updated draws array, but the
// external API fetch must only happen once per build. Memoize it so whichever loader runs
// first triggers the update and the other reuses the same resolved array.
let updatedDrawsPromise: Promise<Draw[]> | null = null;
// Test-only escape hatch: each `it()` block in the same test file shares this module's
// state, so tests that mock loadDrawsWithUpdates/fs differently per case must reset the
// memoized promise between runs.
export function __resetDrawsCacheForTests(): void {
  updatedDrawsPromise = null;
}
function ensureDrawsUpdated(): Promise<Draw[]> {
  if (!updatedDrawsPromise) {
    updatedDrawsPromise = (async () => {
      const existingDraws = readDraws();
      const draws = await loadDrawsWithUpdates(existingDraws);
      if (draws !== existingDraws) {
        writeDraws(draws);
      }
      return draws;
    })();
  }
  return updatedDrawsPromise;
}

const drawSchema = z.object({
  drwNo: z.number(),
  numbers: z.array(z.number()).length(6),
  date: z.string(),
  bonusNo: z.number(),
  firstPrizeAmount: z.number().optional(),
});

export const drawsLoader: Loader = {
  name: "draws-loader",
  load: async ({ store }) => {
    const draws = await ensureDrawsUpdated();
    store.clear();
    for (const draw of draws) {
      store.set({ id: String(draw.drwNo), data: { ...draw } });
    }
  },
};

const draws = defineCollection({
  loader: drawsLoader,
  schema: drawSchema,
});

const predictionOptionSchema = z.object({
  predictions: z.array(z.array(z.number())),
});

const predictionSchema = z.object({
  file: z.string(),
  based_on_drwNo: z.number(),
  generated_at: z.string(),
  option1: predictionOptionSchema,
  option2: predictionOptionSchema.nullable(),
});

export const predictionsLoader: Loader = {
  name: "predictions-loader",
  load: async ({ store }) => {
    const draws = await ensureDrawsUpdated();
    generateAndSavePredictions(draws, {
      rulesPath: RULES_PATH,
      rules2Path: RULES_2_PATH,
      outputDir: PREDICTIONS_DIR,
    });

    const all = listAllPredictions(PREDICTIONS_DIR);
    store.clear();
    for (const { filename, data } of all) {
      store.set({ id: filename, data: { file: filename, ...data } });
    }
  },
};

const predictions = defineCollection({
  loader: predictionsLoader,
  schema: predictionSchema,
});

export const collections = { draws, predictions };
