const API_URL = "https://www.dhlottery.co.kr/lt645/selectPstLt645InfoNew.do";
const HEADERS = {
  "User-Agent": "Mozilla/5.0",
  "X-Requested-With": "XMLHttpRequest",
};
const PAGE_SIZE = 10;
const TIMEOUT_MS = 10_000;

export interface Draw {
  drwNo: number;
  numbers: number[];
  date: string;
  bonusNo: number;
  firstPrizeAmount: number;
}

interface ApiItem {
  ltEpsd: number;
  ltRflYmd: string;
  tm1WnNo: number;
  tm2WnNo: number;
  tm3WnNo: number;
  tm4WnNo: number;
  tm5WnNo: number;
  tm6WnNo: number;
  bnsWnNo: number;
  rnk1WnAmt: number;
}

async function fetchList(params: Record<string, string>): Promise<ApiItem[]> {
  const url = new URL(API_URL);
  for (const [key, value] of Object.entries(params)) {
    url.searchParams.set(key, value);
  }
  const resp = await fetch(url, { headers: HEADERS, signal: AbortSignal.timeout(TIMEOUT_MS) });
  if (!resp.ok) {
    throw new Error(`API request failed with status ${resp.status}`);
  }
  const body = await resp.json();
  return body?.data?.list ?? [];
}

export function fetchOlderPage(cursor: number): Promise<ApiItem[]> {
  return fetchList({ srchDir: "older", srchCursorLtEpsd: String(cursor) });
}

export function fetchCenter(epsd: number): Promise<ApiItem[]> {
  return fetchList({ srchDir: "center", srchLtEpsd: String(epsd) });
}

export function itemToDraw(item: ApiItem): Draw {
  const ymd = item.ltRflYmd;
  return {
    drwNo: item.ltEpsd,
    date: `${ymd.slice(0, 4)}-${ymd.slice(4, 6)}-${ymd.slice(6, 8)}`,
    numbers: [item.tm1WnNo, item.tm2WnNo, item.tm3WnNo, item.tm4WnNo, item.tm5WnNo, item.tm6WnNo],
    bonusNo: item.bnsWnNo,
    firstPrizeAmount: item.rnk1WnAmt,
  };
}

export async function collectNewDraws(draws: Draw[]): Promise<Draw[]> {
  const lastDrwNo = draws.reduce((max, d) => Math.max(max, d.drwNo), 0);
  let cursor = lastDrwNo + PAGE_SIZE + 1;
  const newByNo = new Map<number, Draw>();

  // 1) bulk backfill via "older" pagination
  while (true) {
    const page = await fetchOlderPage(cursor);
    if (page.length === 0) break;
    for (const item of page) {
      const draw = itemToDraw(item);
      if (draw.drwNo > lastDrwNo) {
        newByNo.set(draw.drwNo, draw);
      }
    }
    const topNo = Math.max(...page.map((item) => item.ltEpsd));
    const fullPage = page.length === PAGE_SIZE && topNo === cursor - 1;
    if (!fullPage) break;
    cursor += PAGE_SIZE;
  }

  // 2) probe forward for freshly-announced rounds not yet in "older" listing
  const latestKnown = Math.max(lastDrwNo, ...Array.from(newByNo.keys()));
  let probe = latestKnown + 1;
  while (true) {
    const centerList = await fetchCenter(probe);
    const match = centerList.find((item) => item.ltEpsd === probe);
    if (!match) break;
    newByNo.set(probe, itemToDraw(match));
    probe += 1;
  }

  return Array.from(newByNo.values()).sort((a, b) => a.drwNo - b.drwNo);
}

export async function loadDrawsWithUpdates(existingDraws: Draw[]): Promise<Draw[]> {
  try {
    const newDraws = await collectNewDraws(existingDraws);
    if (newDraws.length === 0) return existingDraws;
    return [...existingDraws, ...newDraws];
  } catch (err) {
    console.warn("동행복권 API 수집 실패, 기존 데이터 유지:", err);
    return existingDraws;
  }
}
