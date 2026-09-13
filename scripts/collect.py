"""동행복권 회차별 당첨번호를 수집해 data/draws.json에 누적 저장한다."""
import json
import sys
from pathlib import Path

import requests

API_URL = "https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={drw_no}"
DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "draws.json"
TIMEOUT_SEC = 10


def load_draws(path: Path = DATA_PATH) -> list[dict]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def save_draws(draws: list[dict], path: Path = DATA_PATH) -> None:
    path.write_text(json.dumps(draws, ensure_ascii=False, indent=2), encoding="utf-8")


def fetch_draw(drw_no: int) -> dict | None:
    resp = requests.get(API_URL.format(drw_no=drw_no), timeout=TIMEOUT_SEC)
    resp.raise_for_status()
    try:
        body = resp.json()
    except requests.exceptions.JSONDecodeError:
        print(f"drwNo={drw_no}: JSON 응답 아님 (차단/점검 페이지로 추정), 스킵", file=sys.stderr)
        return None
    if body.get("returnValue") != "success":
        return None
    numbers = [body[f"drwtNo{i}"] for i in range(1, 7)]
    return {
        "drwNo": body["drwNo"],
        "date": body["drwNoDate"],
        "numbers": numbers,
        "bonusNo": body["bnusNo"],
    }


def collect_new_draws(draws: list[dict]) -> list[dict]:
    last_drw_no = max((d["drwNo"] for d in draws), default=0)
    next_drw_no = last_drw_no + 1
    new_draws = []
    while True:
        draw = fetch_draw(next_drw_no)
        if draw is None:
            break
        new_draws.append(draw)
        next_drw_no += 1
    return new_draws


def main() -> None:
    draws = load_draws()
    new_draws = collect_new_draws(draws)
    if not new_draws:
        print("신규 회차 없음 (아직 발표 전이거나 최신 상태)")
        return
    draws.extend(new_draws)
    save_draws(draws)
    print(f"{len(new_draws)}개 회차 추가됨 (최신 회차: {draws[-1]['drwNo']})")


if __name__ == "__main__":
    main()
