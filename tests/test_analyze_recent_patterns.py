import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from analyze_recent_patterns import (  # noqa: E402
    max_consecutive,
    odd_count,
    zone_count,
    zone_stats,
)


def make_draw(drw_no: int, numbers: list[int]) -> dict:
    return {"drwNo": drw_no, "date": "2026-01-01", "numbers": numbers, "bonusNo": 1}


def test_zone_count_counts_numbers_in_range():
    assert zone_count([1, 5, 9, 10, 20, 45], (1, 9)) == 3
    assert zone_count([1, 5, 9, 10, 20, 45], (40, 45)) == 1
    assert zone_count([1, 2, 3, 4, 5, 6], (40, 45)) == 0


def test_odd_count():
    assert odd_count([1, 2, 3, 4, 5, 6]) == 3
    assert odd_count([2, 4, 6, 8, 10, 12]) == 0


def test_max_consecutive():
    assert max_consecutive([1, 2, 3, 10, 20, 30]) == 3
    assert max_consecutive([1, 3, 5, 7, 9, 11]) == 1
    assert max_consecutive([5, 6, 20, 21, 22, 23]) == 4


def test_zone_stats_zero_pct_matches_manual_count():
    draws = [
        make_draw(1, [1, 2, 3, 4, 5, 6]),          # 40~45 구간 0개
        make_draw(2, [1, 2, 3, 4, 5, 41]),         # 40~45 구간 1개
        make_draw(3, [1, 2, 3, 4, 40, 41]),        # 40~45 구간 2개
        make_draw(4, [7, 8, 9, 10, 11, 12]),       # 40~45 구간 0개
    ]
    stats = zone_stats(draws, [(40, 45)])
    label_stats = stats["40~45"]

    assert label_stats["zero_pct"] == 50.0  # 4개 중 2개가 0개
    assert label_stats["min"] == 0
    assert label_stats["max"] == 2
    assert label_stats["avg"] == (0 + 1 + 2 + 0) / 4
