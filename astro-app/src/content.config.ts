import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";
import { defineCollection, z } from "astro:content";
import type { Loader } from "astro/loaders";
import { loadDrawsWithUpdates, type Draw } from "./content/loaders/draws-loader";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
export const DRAWS_PATH = path.resolve(__dirname, "../../data/draws.json");

export function readDraws(filePath: string = DRAWS_PATH): Draw[] {
  if (!existsSync(filePath)) return [];
  return JSON.parse(readFileSync(filePath, "utf-8"));
}

export function writeDraws(draws: Draw[], filePath: string = DRAWS_PATH): void {
  writeFileSync(filePath, JSON.stringify(draws, null, 2), "utf-8");
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
    const existingDraws = readDraws();
    const draws = await loadDrawsWithUpdates(existingDraws);
    if (draws !== existingDraws) {
      writeDraws(draws);
    }

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

export const collections = { draws };
