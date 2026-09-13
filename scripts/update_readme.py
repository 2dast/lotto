"""predictions/ 폴더의 최신 예측 파일을 README.md 마커 구간에 반영한다."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README_PATH = ROOT / "README.md"
PREDICTIONS_DIR = ROOT / "predictions"

START_MARKER = "<!-- PREDICTION:START -->"
END_MARKER = "<!-- PREDICTION:END -->"


def find_latest_predictions_file(dir_path: Path = PREDICTIONS_DIR) -> Path:
    files = list(dir_path.glob("round_*/predictions_*.json"))
    if not files:
        raise FileNotFoundError(f"{dir_path}에 round_<회차>/predictions_*.json 파일이 없습니다")
    # 파일명의 회차 번호가 zero-padding 없이 들어가 이름순 정렬은 신뢰할 수 없다.
    # generated_at(ISO8601) 값으로 정렬해 진짜 최신 파일을 고른다.
    candidates = [(json.loads(p.read_text(encoding="utf-8"))["generated_at"], p) for p in files]
    return max(candidates, key=lambda c: c[0])[1]


def build_block(data: dict) -> str:
    lines = [
        START_MARKER,
        f"- {data['based_on_drwNo'] + 1}회차 예측",
        f"- 생성 시각: {data['generated_at']}",
        "",
    ]
    for i, combo in enumerate(data["predictions"], start=1):
        numbers = ", ".join(str(n) for n in combo)
        lines.append(f"{i}. {numbers}")
    lines.append(END_MARKER)
    return "\n".join(lines)


def main() -> None:
    latest_path = find_latest_predictions_file()
    data = json.loads(latest_path.read_text(encoding="utf-8"))
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
