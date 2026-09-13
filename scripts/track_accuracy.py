"""매 실행마다 data/draws.json의 최신 실제 회차와, 그 직전 회차를 기준으로
생성됐던 predictions/predictions_<ts>.json의 5세트를 비교해 적중개수를
data/accuracy_history.json에 누적 기록한다.

같은 based_on_drwNo로 여러 predictions_*.json이 있으면(수동 재실행 등)
generated_at이 가장 늦은 파일만 공식 예측으로 채택한다.
이미 기록된 drwNo는 다시 추가하지 않는다(idempotent).
아직 비교할 실제 결과가 없으면(다음 회차 미추첨) 조용히 종료한다.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "draws.json"
PREDICTIONS_DIR = ROOT / "predictions"
HISTORY_PATH = ROOT / "data" / "accuracy_history.json"


def compute_hits(predictions: list[list[int]], actual: list[int]) -> list[int]:
    actual_set = set(actual)
    return [len(set(combo) & actual_set) for combo in predictions]


def load_history() -> list[dict]:
    if not HISTORY_PATH.exists():
        return []
    return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))


def latest_prediction_for(based_on_drwNo: int) -> tuple[str, dict] | None:
    candidates = []
    for path in PREDICTIONS_DIR.glob("predictions_*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("based_on_drwNo") == based_on_drwNo:
            candidates.append((data["generated_at"], path.name, data))
    if not candidates:
        return None
    candidates.sort(key=lambda c: c[0])
    _, name, data = candidates[-1]
    return name, data


def main() -> None:
    draws = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    latest = draws[-1]
    drw_no = latest["drwNo"]

    history = load_history()
    if any(entry["drwNo"] == drw_no for entry in history):
        print(f"{drw_no}회차는 이미 기록되어 있습니다.")
        return

    found = latest_prediction_for(drw_no - 1)
    if found is None:
        print(f"{drw_no - 1}회차 기준 예측 파일이 없어 적중 이력을 기록하지 않습니다.")
        return

    pred_filename, pred_data = found
    hits = compute_hits(pred_data["predictions"], latest["numbers"])

    history.append({
        "drwNo": drw_no,
        "date": latest["date"],
        "predictions_file": pred_filename,
        "hits": hits,
    })
    history.sort(key=lambda entry: entry["drwNo"])
    HISTORY_PATH.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{drw_no}회차 적중 이력 기록됨: {hits} ({pred_filename})")


if __name__ == "__main__":
    main()
