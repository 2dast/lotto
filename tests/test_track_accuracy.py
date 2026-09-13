import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import track_accuracy  # noqa: E402


def test_compute_hits_counts_intersection():
    predictions = [[1, 2, 3, 4, 5, 6], [7, 8, 9, 10, 11, 12]]
    actual = [1, 2, 3, 40, 41, 42]
    assert track_accuracy.compute_hits(predictions, actual) == [3, 0]


def test_main_appends_history_once_then_skips_duplicate(tmp_path, monkeypatch):
    data_path = tmp_path / "draws.json"
    predictions_dir = tmp_path / "predictions"
    history_path = tmp_path / "accuracy_history.json"
    predictions_dir.mkdir()

    draws = [
        {"drwNo": 1240, "date": "2026-09-05", "numbers": [1, 2, 3, 4, 5, 6], "bonusNo": 7},
        {"drwNo": 1241, "date": "2026-09-12", "numbers": [1, 2, 3, 40, 41, 42], "bonusNo": 8},
    ]
    data_path.write_text(json.dumps(draws), encoding="utf-8")

    pred_file = predictions_dir / "predictions_20260906_000000.json"
    pred_file.write_text(json.dumps({
        "based_on_drwNo": 1240,
        "generated_at": "2026-09-06T00:00:00",
        "predictions": [[1, 2, 3, 4, 5, 6], [7, 8, 9, 10, 11, 12]],
    }), encoding="utf-8")

    monkeypatch.setattr(track_accuracy, "DATA_PATH", data_path)
    monkeypatch.setattr(track_accuracy, "PREDICTIONS_DIR", predictions_dir)
    monkeypatch.setattr(track_accuracy, "HISTORY_PATH", history_path)

    track_accuracy.main()
    history = json.loads(history_path.read_text(encoding="utf-8"))
    assert len(history) == 1
    assert history[0]["drwNo"] == 1241
    assert history[0]["hits"] == [3, 0]

    # 같은 drwNo로 재실행해도 중복 추가되지 않는다
    track_accuracy.main()
    history = json.loads(history_path.read_text(encoding="utf-8"))
    assert len(history) == 1


def test_main_skips_silently_when_no_matching_prediction(tmp_path, monkeypatch):
    data_path = tmp_path / "draws.json"
    predictions_dir = tmp_path / "predictions"
    history_path = tmp_path / "accuracy_history.json"
    predictions_dir.mkdir()

    draws = [{"drwNo": 1241, "date": "2026-09-12", "numbers": [1, 2, 3, 40, 41, 42], "bonusNo": 8}]
    data_path.write_text(json.dumps(draws), encoding="utf-8")

    monkeypatch.setattr(track_accuracy, "DATA_PATH", data_path)
    monkeypatch.setattr(track_accuracy, "PREDICTIONS_DIR", predictions_dir)
    monkeypatch.setattr(track_accuracy, "HISTORY_PATH", history_path)

    track_accuracy.main()
    assert not history_path.exists()
