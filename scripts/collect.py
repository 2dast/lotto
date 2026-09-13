"""동행복권 회차별 당첨번호를 수집해 data/draws.json에 누적 저장한다.

2026년 1월 사이트 개편으로 기존 getLottoNumber API가 막혀,
결과 페이지(/lt645/result)가 실제로 호출하는 내부 API로 교체했다.
"""
import json
import sys
from pathlib import Path

import requests

API_URL = "https://www.dhlottery.co.kr/lt645/selectPstLt645InfoNew.do"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "X-Requested-With": "XMLHttpRequest",
}
DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "draws.json"
TIMEOUT_SEC = 10
PAGE_SIZE = 10  # API가 한 번에 내려주는 회차 수


def load_draws(path: Path = DATA_PATH) -> list[dict]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def save_draws(draws: list[dict], path: Path = DATA_PATH) -> None:
    path.write_text(json.dumps(draws, ensure_ascii=False, indent=2), encoding="utf-8")


def fetch_page(cursor: int) -> list[dict]:
    """cursor보다 작은 회차 중 최신 10개를 내림차순으로 반환한다. 없으면 빈 리스트."""
    resp = requests.get(
        API_URL,
        params={"srchDir": "older", "srchCursorLtEpsd": str(cursor)},
        headers=HEADERS,
        timeout=TIMEOUT_SEC,
    )
    resp.raise_for_status()
    body = resp.json()
    return body.get("data", {}).get("list") or []


def item_to_draw(item: dict) -> dict:
    ymd = item["ltRflYmd"]
    return {
        "drwNo": item["ltEpsd"],
        "date": f"{ymd[0:4]}-{ymd[4:6]}-{ymd[6:8]}",
        "numbers": [item[f"tm{i}WnNo"] for i in range(1, 7)],
        "bonusNo": item["bnsWnNo"],
    }


def collect_new_draws(draws: list[dict]) -> list[dict]:
    last_drw_no = max((d["drwNo"] for d in draws), default=0)
    cursor = last_drw_no + PAGE_SIZE + 1
    new_by_no: dict[int, dict] = {}

    while True:
        page = fetch_page(cursor)
        if not page:
            break
        for item in page:
            draw = item_to_draw(item)
            if draw["drwNo"] > last_drw_no:
                new_by_no[draw["drwNo"]] = draw

        top_no = max(item["ltEpsd"] for item in page)
        full_page = len(page) == PAGE_SIZE and top_no == cursor - 1
        if not full_page:
            break
        cursor += PAGE_SIZE

    return sorted(new_by_no.values(), key=lambda d: d["drwNo"])


def main() -> None:
    draws = load_draws()
    try:
        new_draws = collect_new_draws(draws)
    except requests.exceptions.JSONDecodeError:
        print("API 응답이 JSON이 아님 (차단/점검 페이지로 추정), 스킵", file=sys.stderr)
        return
    if not new_draws:
        print("신규 회차 없음 (아직 발표 전이거나 최신 상태)")
        return
    draws.extend(new_draws)
    save_draws(draws)
    print(f"{len(new_draws)}개 회차 추가됨 (최신 회차: {draws[-1]['drwNo']})")


if __name__ == "__main__":
    main()
