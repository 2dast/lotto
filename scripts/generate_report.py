"""scripts/report_template.html을 바탕으로 predictions/의 최신 추천 번호를 채워
reports/lotto_report_<타임스탬프>.html로 저장한다. 매 실행마다 새 파일을 남겨
이력으로 쌓이며, 템플릿 자체는 건드리지 않는다.

리포트는 RULES.md 조건표 + 추천 세트 스크리닝표만 다루므로, data/draws.json에서는
총 회차 수만 있으면 된다 (분포/백테스트 계산은 하지 않음).
"""
import datetime as dt
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "draws.json"
TEMPLATE_PATH = ROOT / "scripts" / "report_template.html"
PREDICTIONS_DIR = ROOT / "predictions"
REPORT_DIR = ROOT / "reports"

KST = dt.timezone(dt.timedelta(hours=9))


def set_span(html: str, span_id: str, value: str) -> str:
    pattern = re.compile(rf'(id="{span_id}">)[^<]*(<)')
    new_html, n = pattern.subn(rf"\g<1>{value}\g<2>", html)
    if n == 0:
        raise ValueError(f"id={span_id!r} 스팬을 리포트에서 찾을 수 없습니다")
    return new_html


def load_latest_predictions() -> tuple[str, dict]:
    files = sorted(PREDICTIONS_DIR.glob("predictions_*.json"))
    if not files:
        raise FileNotFoundError("predictions/predictions_*.json이 없습니다. scripts/predict.py를 먼저 실행하세요")
    latest = files[-1]
    return latest.name, json.loads(latest.read_text(encoding="utf-8"))


def main() -> None:
    draws = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    total = len(draws)
    pred_filename, pred_data = load_latest_predictions()
    based_on = pred_data["based_on_drwNo"]

    data_obj = {"predictions": pred_data["predictions"]}

    html = TEMPLATE_PATH.read_text(encoding="utf-8")
    html = re.sub(
        r"const DATA = \{.*?\};",
        "const DATA = " + json.dumps(data_obj, ensure_ascii=False) + ";",
        html,
        count=1,
        flags=re.DOTALL,
    )

    today = dt.datetime.now(KST).strftime("%Y.%m.%d")

    html = set_span(html, "f-date", today)
    html = set_span(html, "f-total", str(total))
    html = set_span(html, "f-total2", str(total))
    html = set_span(html, "f-count", f"{total:,}")
    html = set_span(html, "f-basedon", str(based_on))
    html = set_span(html, "f-basedon2", str(based_on + 1))
    html = set_span(html, "f-basedon3", str(based_on + 1))
    html = set_span(html, "f-basedon4", str(based_on + 1))
    html = set_span(html, "f-predfile", pred_filename)

    # predictions_<ts>.json 의 타임스탬프를 그대로 리포트 파일명에 붙여 1:1로 이력 관리
    ts = pred_filename.removeprefix("predictions_").removesuffix(".json")
    REPORT_DIR.mkdir(exist_ok=True)
    report_path = REPORT_DIR / f"lotto_report_{ts}.html"
    report_path.write_text(html, encoding="utf-8")
    print(f"리포트 생성됨 -> {report_path} (총 {total}회차, 기준회차 {based_on})")


if __name__ == "__main__":
    main()
