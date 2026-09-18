import { describe, it, expect, vi, afterEach } from "vitest";
import {
  fetchOlderPage,
  fetchCenter,
  itemToDraw,
  collectNewDraws,
  loadDrawsWithUpdates,
  type Draw,
} from "./draws-loader";

function jsonResponse(body: unknown, ok = true) {
  return {
    ok,
    json: async () => body,
  } as Response;
}

function makeItem(epsd: number, ymd: string) {
  return {
    ltEpsd: epsd,
    ltRflYmd: ymd,
    tm1WnNo: 1,
    tm2WnNo: 2,
    tm3WnNo: 3,
    tm4WnNo: 4,
    tm5WnNo: 5,
    tm6WnNo: 6,
    bnsWnNo: 7,
    rnk1WnAmt: 1000000000,
  };
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("itemToDraw", () => {
  it("maps API item fields to Draw shape", () => {
    const item = makeItem(1100, "20240101");
    const draw = itemToDraw(item);
    expect(draw).toEqual<Draw>({
      drwNo: 1100,
      date: "2024-01-01",
      numbers: [1, 2, 3, 4, 5, 6],
      bonusNo: 7,
      firstPrizeAmount: 1000000000,
    });
  });
});

describe("fetchOlderPage / fetchCenter", () => {
  it("fetchOlderPage sends srchDir=older and srchCursorLtEpsd, returns list", async () => {
    const fetchMock = vi.fn(async (url: string | URL, init?: RequestInit) => {
      const u = new URL(url.toString());
      expect(u.searchParams.get("srchDir")).toBe("older");
      expect(u.searchParams.get("srchCursorLtEpsd")).toBe("1111");
      return jsonResponse({ data: { list: [makeItem(1110, "20240101")] } });
    });
    vi.stubGlobal("fetch", fetchMock);
    const list = await fetchOlderPage(1111);
    expect(list).toHaveLength(1);
    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [, init] = fetchMock.mock.calls[0];
    expect(init?.headers).toMatchObject({
      "User-Agent": "Mozilla/5.0",
      "X-Requested-With": "XMLHttpRequest",
    });
  });

  it("fetchCenter sends srchDir=center and srchLtEpsd, returns list", async () => {
    const fetchMock = vi.fn(async (url: string | URL, init?: RequestInit) => {
      const u = new URL(url.toString());
      expect(u.searchParams.get("srchDir")).toBe("center");
      expect(u.searchParams.get("srchLtEpsd")).toBe("1200");
      return jsonResponse({ data: { list: [makeItem(1200, "20240201")] } });
    });
    vi.stubGlobal("fetch", fetchMock);
    const list = await fetchCenter(1200);
    expect(list).toHaveLength(1);
  });

  it("returns empty list when data.list is missing", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => jsonResponse({ data: {} }))
    );
    expect(await fetchOlderPage(1)).toEqual([]);
  });
});

describe("collectNewDraws", () => {
  it("merges multiple older-pagination pages until a non-full page ends it", async () => {
    // existing draws end at 1100. PAGE_SIZE=10, so cursor starts at 1111.
    const existing: Draw[] = [
      { drwNo: 1100, date: "2024-01-01", numbers: [1, 2, 3, 4, 5, 6], bonusNo: 7, firstPrizeAmount: 1 },
    ];

    // Page 1: cursor=1111 -> full page descending 1110..1101 (10 items), top=1110=cursor-1
    const page1 = Array.from({ length: 10 }, (_, i) => makeItem(1110 - i, "20240101"));
    // Page 2: cursor=1121 -> partial page (not full) -> stop after this
    const page2 = [makeItem(1112, "20240102"), makeItem(1111, "20240102")];

    const fetchMock = vi.fn(async (url: string | URL, init?: RequestInit) => {
      const u = new URL(url.toString());
      if (u.searchParams.get("srchDir") === "older") {
        const cursor = u.searchParams.get("srchCursorLtEpsd");
        if (cursor === "1111") return jsonResponse({ data: { list: page1 } });
        if (cursor === "1121") return jsonResponse({ data: { list: page2 } });
        return jsonResponse({ data: { list: [] } });
      }
      if (u.searchParams.get("srchDir") === "center") {
        // no fresh round beyond latest known (1112)
        return jsonResponse({ data: { list: [] } });
      }
      throw new Error("unexpected request");
    });
    vi.stubGlobal("fetch", fetchMock);

    const result = await collectNewDraws(existing);
    const nos = result.map((d) => d.drwNo);
    expect(nos).toEqual([1101, 1102, 1103, 1104, 1105, 1106, 1107, 1108, 1109, 1110, 1111, 1112]);
  });

  it("picks up a freshly announced round via center-probe not yet in older listing", async () => {
    const existing: Draw[] = [
      { drwNo: 1100, date: "2024-01-01", numbers: [1, 2, 3, 4, 5, 6], bonusNo: 7, firstPrizeAmount: 1 },
    ];

    const fetchMock = vi.fn(async (url: string | URL, init?: RequestInit) => {
      const u = new URL(url.toString());
      if (u.searchParams.get("srchDir") === "older") {
        // no older pages available at all
        return jsonResponse({ data: { list: [] } });
      }
      if (u.searchParams.get("srchDir") === "center") {
        const epsd = Number(u.searchParams.get("srchLtEpsd"));
        if (epsd === 1101) {
          return jsonResponse({ data: { list: [makeItem(1101, "20240108")] } });
        }
        return jsonResponse({ data: { list: [] } });
      }
      throw new Error("unexpected request");
    });
    vi.stubGlobal("fetch", fetchMock);

    const result = await collectNewDraws(existing);
    expect(result).toEqual([
      { drwNo: 1101, date: "2024-01-08", numbers: [1, 2, 3, 4, 5, 6], bonusNo: 7, firstPrizeAmount: 1000000000 },
    ]);
  });
});

describe("loadDrawsWithUpdates", () => {
  const existing: Draw[] = [
    { drwNo: 1100, date: "2024-01-01", numbers: [1, 2, 3, 4, 5, 6], bonusNo: 7, firstPrizeAmount: 1 },
  ];

  it("falls back to existing draws unchanged when fetch rejects (network error)", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => {
        throw new Error("network down");
      })
    );
    const result = await loadDrawsWithUpdates(existing);
    expect(result).toEqual(existing);
  });

  it("falls back to existing draws unchanged when fetch aborts due to timeout", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => {
        const err = new DOMException("The operation was aborted.", "TimeoutError");
        throw err;
      })
    );
    const result = await loadDrawsWithUpdates(existing);
    expect(result).toEqual(existing);
  });

  it("falls back to existing draws unchanged when response is not ok", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => jsonResponse({}, false))
    );
    const result = await loadDrawsWithUpdates(existing);
    expect(result).toEqual(existing);
  });

  it("falls back to existing draws unchanged when response body is not JSON", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => ({
        ok: true,
        json: async () => {
          throw new SyntaxError("Unexpected token");
        },
      }))
    );
    const result = await loadDrawsWithUpdates(existing);
    expect(result).toEqual(existing);
  });

  it("returns existing plus new draws when collection succeeds", async () => {
    const fetchMock = vi.fn(async (url: string | URL, init?: RequestInit) => {
      const u = new URL(url.toString());
      if (u.searchParams.get("srchDir") === "older") {
        return jsonResponse({ data: { list: [] } });
      }
      return jsonResponse({ data: { list: [] } });
    });
    vi.stubGlobal("fetch", fetchMock);
    const result = await loadDrawsWithUpdates(existing);
    expect(result).toEqual(existing);
  });
});
