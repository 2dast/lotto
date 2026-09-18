import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { readFileSync, writeFileSync, existsSync, mkdtempSync, rmSync } from "node:fs";
import path from "node:path";
import os from "node:os";
import type { Draw } from "./content/loaders/draws-loader";

// content.config.ts reads/writes the real repo-root data/draws.json via readDraws/writeDraws
// defaults. Wrap existsSync/readFileSync/writeFileSync so the "drawsLoader.load" tests below
// can stub them and NEVER touch the real file, while other tests in this file (which pass
// explicit temp file paths) keep calling through to the real implementation by default.
vi.mock("node:fs", async () => {
  const actual = await vi.importActual<typeof import("node:fs")>("node:fs");
  return {
    ...actual,
    existsSync: vi.fn(actual.existsSync),
    readFileSync: vi.fn(actual.readFileSync),
    writeFileSync: vi.fn(actual.writeFileSync),
  };
});

// "astro:content" is a virtual module only resolvable inside Astro's build/dev
// pipeline. Stub it so content.config.ts can be imported in plain Vitest.
vi.mock("astro:content", () => {
  const chainable = () => ({
    length: () => chainable(),
    optional: () => chainable(),
  });
  return {
    defineCollection: (config: unknown) => config,
    z: {
      object: () => chainable(),
      number: () => chainable(),
      string: () => chainable(),
      array: () => chainable(),
    },
  };
});

vi.mock("./content/loaders/draws-loader", async () => {
  const actual = await vi.importActual<typeof import("./content/loaders/draws-loader")>(
    "./content/loaders/draws-loader"
  );
  return {
    ...actual,
    loadDrawsWithUpdates: vi.fn(),
  };
});

const { readDraws, writeDraws, drawsLoader } = await import("./content.config");
const { loadDrawsWithUpdates } = await import("./content/loaders/draws-loader");
const mockedLoadDrawsWithUpdates = vi.mocked(loadDrawsWithUpdates);

describe("readDraws / writeDraws", () => {
  let tmpDir: string;
  let filePath: string;

  beforeEach(() => {
    tmpDir = mkdtempSync(path.join(os.tmpdir(), "draws-test-"));
    filePath = path.join(tmpDir, "draws.json");
  });

  afterEach(() => {
    rmSync(tmpDir, { recursive: true, force: true });
  });

  it("returns empty array when file does not exist", () => {
    expect(readDraws(path.join(tmpDir, "missing.json"))).toEqual([]);
  });

  it("reads existing draws from file", () => {
    const existing: Draw[] = [
      { drwNo: 1, numbers: [1, 2, 3, 4, 5, 6], date: "2002-12-07", bonusNo: 7, firstPrizeAmount: 100 },
    ];
    writeFileSync(filePath, JSON.stringify(existing, null, 2), "utf-8");
    expect(readDraws(filePath)).toEqual(existing);
  });

  it("writes draws back to file in pretty-printed JSON", () => {
    const draws: Draw[] = [
      { drwNo: 2, numbers: [1, 2, 3, 4, 5, 6], date: "2002-12-14", bonusNo: 8, firstPrizeAmount: 200 },
    ];
    writeDraws(draws, filePath);
    const raw = readFileSync(filePath, "utf-8");
    expect(JSON.parse(raw)).toEqual(draws);
    expect(raw).toBe(JSON.stringify(draws, null, 2));
  });

  it("merges existing draws with loadDrawsWithUpdates result (mocked)", async () => {
    const existing: Draw[] = [
      { drwNo: 1, numbers: [1, 2, 3, 4, 5, 6], date: "2002-12-07", bonusNo: 7, firstPrizeAmount: 100 },
    ];
    writeFileSync(filePath, JSON.stringify(existing, null, 2), "utf-8");

    const newDraw: Draw = { drwNo: 2, numbers: [7, 8, 9, 10, 11, 12], date: "2002-12-14", bonusNo: 13, firstPrizeAmount: 300 };
    const mockLoad = vi.fn(async (draws: Draw[]) => [...draws, newDraw]);

    const before = readDraws(filePath);
    const merged = await mockLoad(before);
    writeDraws(merged, filePath);

    expect(mockLoad).toHaveBeenCalledWith(existing);
    expect(readDraws(filePath)).toEqual([...existing, newDraw]);
  });
});

describe("drawsLoader.load", () => {
  const fixtureDraws: Draw[] = [
    { drwNo: 1, numbers: [1, 2, 3, 4, 5, 6], date: "2002-12-07", bonusNo: 7, firstPrizeAmount: 100 },
    { drwNo: 2, numbers: [7, 8, 9, 10, 11, 12], date: "2002-12-14", bonusNo: 13, firstPrizeAmount: 300 },
  ];

  beforeEach(() => {
    mockedLoadDrawsWithUpdates.mockReset();
    // drawsLoader.load() reads/writes the real DRAWS_PATH internally via readDraws/writeDraws
    // defaults — stub the mocked node:fs functions so this test NEVER touches the real
    // data/draws.json on disk, regardless of the path drawsLoader.load resolves internally.
    vi.mocked(existsSync).mockReturnValue(true);
    vi.mocked(readFileSync).mockReturnValue("[]");
    vi.mocked(writeFileSync).mockImplementation(() => undefined);
  });

  afterEach(() => {
    vi.mocked(existsSync).mockReset();
    vi.mocked(readFileSync).mockReset();
    vi.mocked(writeFileSync).mockReset();
  });

  it("clears the store and sets an entry per draw returned by loadDrawsWithUpdates", async () => {
    mockedLoadDrawsWithUpdates.mockResolvedValue(fixtureDraws);

    const store = {
      clear: vi.fn(),
      set: vi.fn(),
    };

    await drawsLoader.load({ store } as any);

    // node:fs writeFileSync is stubbed above, so this call never touches the real
    // data/draws.json on disk even though it's invoked with that path.
    expect(vi.mocked(writeFileSync)).toHaveBeenCalledTimes(1);

    expect(store.clear).toHaveBeenCalledTimes(1);
    expect(store.set).toHaveBeenCalledTimes(2);
    expect(store.set).toHaveBeenNthCalledWith(1, { id: "1", data: { ...fixtureDraws[0] } });
    expect(store.set).toHaveBeenNthCalledWith(2, { id: "2", data: { ...fixtureDraws[1] } });

    // clear() must run before any set() call
    const clearOrder = store.clear.mock.invocationCallOrder[0];
    const firstSetOrder = store.set.mock.invocationCallOrder[0];
    expect(clearOrder).toBeLessThan(firstSetOrder);
  });
});
