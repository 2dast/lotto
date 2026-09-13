"""predictions.json의 최신 예측을 README.md 마커 구간에 반영한다."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README_PATH = ROOT / "README.md"
PREDICTIONS_PATH = ROOT / "predictions.json"

START_MARKER = "<!-- PREDICTION:START -->"
END_MARKER = "<!-- PREDICTION:END -->"


def build_block(data: dict) -> str:
    lines = [
        START_MARKER,
        f"- 기준 회차: {data['based_on_drwNo']}회 이후 예측",
        f"- 생성 시각: {data['generated_at']}",
        "",
    ]
    for i, combo in enumerate(data["predictions"], start=1):
        numbers = ", ".join(str(n) for n in combo)
        lines.append(f"{i}. {numbers}")
    lines.append(END_MARKER)
    return "\n".join(lines)


def main() -> None:
    data = json.loads(PREDICTIONS_PATH.read_text(encoding="utf-8"))
    readme = README_PATH.read_text(encoding="utf-8")

    pattern = re.compile(
        re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER), re.DOTALL
    )
    new_block = build_block(data)
    if not pattern.search(readme):
        raise ValueError("README.md에서 PREDICTION 마커를 찾을 수 없습니다")

    updated = pattern.sub(new_block, readme)
    README_PATH.write_text(updated, encoding="utf-8")
    print("README.md 갱신 완료")


if __name__ == "__main__":
    main()
