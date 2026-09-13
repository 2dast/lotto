import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from predict import load_rules, passes_filters  # noqa: E402


RULES = load_rules()
FILTERS = RULES["pattern_filters"]


def test_odd_even_ratio_rejects_all_even():
    combo = [2, 4, 6, 8, 10, 12]
    assert not passes_filters(combo, FILTERS)


def test_40s_zone_allows_up_to_two():
    # 40번대 없음 -> 허용 (0~2개 허용)
    combo_no_40s = [3, 10, 20, 21, 29, 34]
    assert passes_filters(combo_no_40s, FILTERS)

    # 40번대 2개 -> 허용
    combo_two_40s = [40, 41, 1, 10, 20, 30]
    assert passes_filters(combo_two_40s, FILTERS)

    # 40번대 3개 -> 거부
    combo_three_40s = [40, 41, 42, 1, 10, 20]
    assert not passes_filters(combo_three_40s, FILTERS)


def test_valid_combo_passes():
    # 홀짝 3:3, 합계 범위 내, 연속 없음, 40번대 1개
    combo = [3, 10, 21, 29, 34, 42]
    assert passes_filters(combo, FILTERS)


def test_max_consecutive_exceeded():
    combo = [1, 12, 13, 14, 15, 30]
    assert not passes_filters(combo, FILTERS)


def test_sum_range_rejects_too_low():
    combo = [1, 2, 3, 4, 5, 41]
    assert not passes_filters(combo, FILTERS)
