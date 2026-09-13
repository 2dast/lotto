import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from collect import collect_new_draws  # noqa: E402


def test_collect_new_draws_stops_on_fail_response():
    existing = [{"drwNo": 1, "date": "2002-12-07", "numbers": [1, 2, 3, 4, 5, 6], "bonusNo": 7}]

    responses = {
        2: {"drwNo": 2, "date": "2002-12-14", "numbers": [10, 11, 12, 13, 14, 15], "bonusNo": 16},
        3: None,  # 아직 발표 안 됨
    }

    def fake_fetch(drw_no):
        return responses.get(drw_no)

    with patch("collect.fetch_draw", side_effect=fake_fetch):
        new_draws = collect_new_draws(existing)

    assert len(new_draws) == 1
    assert new_draws[0]["drwNo"] == 2


def test_collect_new_draws_no_new_data():
    existing = [{"drwNo": 5, "date": "x", "numbers": [1, 2, 3, 4, 5, 6], "bonusNo": 7}]

    with patch("collect.fetch_draw", return_value=None):
        new_draws = collect_new_draws(existing)

    assert new_draws == []
