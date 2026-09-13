import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from collect import collect_new_draws  # noqa: E402


def make_item(ltEpsd: int) -> dict:
    return {
        "ltEpsd": ltEpsd,
        "tm1WnNo": 1, "tm2WnNo": 2, "tm3WnNo": 3,
        "tm4WnNo": 4, "tm5WnNo": 5, "tm6WnNo": 6,
        "bnsWnNo": 7,
        "ltRflYmd": "20260101",
        "rnk1WnAmt": 1000000000,
    }


def test_collect_new_draws_single_partial_page():
    existing = [{"drwNo": 1, "date": "2002-12-07", "numbers": [1, 2, 3, 4, 5, 6], "bonusNo": 7}]

    # cursor=12 요청 시 2번 회차 딱 하나만 존재 (전체 페이지 아님 -> 더 없음으로 판단)
    def fake_fetch_page(cursor):
        if cursor == 12:
            return [make_item(2)]
        return []

    with patch("collect.fetch_page", side_effect=fake_fetch_page), \
         patch("collect.fetch_center", return_value=[]):
        new_draws = collect_new_draws(existing)

    assert [d["drwNo"] for d in new_draws] == [2]


def test_collect_new_draws_no_new_data():
    existing = [{"drwNo": 5, "date": "x", "numbers": [1, 2, 3, 4, 5, 6], "bonusNo": 7}]

    with patch("collect.fetch_page", return_value=[]), \
         patch("collect.fetch_center", return_value=[]):
        new_draws = collect_new_draws(existing)

    assert new_draws == []


def test_collect_new_draws_paginates_over_full_pages():
    existing: list[dict] = []  # last_drw_no=0 -> 첫 cursor=11

    def fake_fetch_page(cursor):
        if cursor == 11:
            return [make_item(n) for n in range(10, 0, -1)]  # 1~10, full page
        if cursor == 21:
            return [make_item(n) for n in range(15, 10, -1)]  # 11~15만 존재, partial page
        return []

    with patch("collect.fetch_page", side_effect=fake_fetch_page), \
         patch("collect.fetch_center", return_value=[]):
        new_draws = collect_new_draws(existing)

    assert [d["drwNo"] for d in new_draws] == list(range(1, 16))


def test_collect_new_draws_finds_latest_round_via_center_probe():
    """'older' 페이지네이션이 아직 안 잡아준 방금 발표된 회차를 center 조회로 찾아낸다."""
    existing = [{"drwNo": 1240, "date": "2026-09-05", "numbers": [1, 2, 3, 4, 5, 6], "bonusNo": 7}]

    def fake_fetch_center(epsd):
        if epsd == 1241:
            return [make_item(1241)]
        return []

    with patch("collect.fetch_page", return_value=[]), \
         patch("collect.fetch_center", side_effect=fake_fetch_center):
        new_draws = collect_new_draws(existing)

    assert [d["drwNo"] for d in new_draws] == [1241]
