"""직전 50회 빈도를 기준으로 hot(고빈도 우대)/cold(저빈도 우대)/neutral(무가중) 전략을
과거 회차에 대해 시뮬레이션하고, 실제 당첨번호와의 평균 일치 개수를 비교한다.
RULES.md/predict.py는 수정하지 않는다.
"""
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "draws.json"

ALL_NUMBERS = list(range(1, 46))
WINDOW = 50
SIMULATIONS_PER_DRAW = 20  # 회차당 시뮬레이션 반복 횟수(가중 샘플링 변동성 완화용)


def load_draws(path: Path = DATA_PATH) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def recent_freq(draws: list[dict], end_idx: int, window: int) -> dict[int, int]:
    """draws[end_idx] 직전 window회(= draws[end_idx-window:end_idx])의 번호별 출현 횟수."""
    count = {n: 0 for n in ALL_NUMBERS}
    for d in draws[max(0, end_idx - window):end_idx]:
        for n in d["numbers"]:
            count[n] += 1
    return count


def weighted_pick(weights: dict[int, float], k: int = 6) -> set[int]:
    pool = list(ALL_NUMBERS)
    picked = []
    for _ in range(k):
        w = [weights[n] + 0.01 for n in pool]
        chosen = random.choices(pool, weights=w, k=1)[0]
        picked.append(chosen)
        pool.remove(chosen)
    return set(picked)


def strategy_weights(freq: dict[int, int], mode: str) -> dict[int, float]:
    if mode == "neutral":
        return {n: 1.0 for n in ALL_NUMBERS}
    max_f = max(freq.values()) or 1
    if mode == "hot":
        return {n: freq[n] / max_f for n in ALL_NUMBERS}
    if mode == "cold":
        return {n: 1.0 - freq[n] / max_f for n in ALL_NUMBERS}
    raise ValueError(mode)


def main() -> None:
    draws = load_draws()
    modes = ["hot", "cold", "neutral"]
    match_totals = {m: 0 for m in modes}
    match_trials = {m: 0 for m in modes}

    for idx in range(WINDOW, len(draws)):
        actual = set(draws[idx]["numbers"])
        freq = recent_freq(draws, idx, WINDOW)
        for mode in modes:
            weights = strategy_weights(freq, mode)
            for _ in range(SIMULATIONS_PER_DRAW):
                picked = weighted_pick(weights)
                match_totals[mode] += len(picked & actual)
                match_trials[mode] += 1

    print(f"분석 대상: {len(draws) - WINDOW}회차 (직전 {WINDOW}회 빈도 기준), 회차당 {SIMULATIONS_PER_DRAW}회 시뮬레이션\n")
    print("[전략별 평균 일치 개수 (6개 중)]")
    for mode in modes:
        avg = match_totals[mode] / match_trials[mode]
        print(f"  {mode:8s}: {avg:.4f}")

    # 이론적 기대값(완전 무작위 6/45 조합의 기대 일치 개수) = 6 * 6/45
    print(f"\n  이론적 기대값(순수 무작위): {6 * 6 / 45:.4f}")


if __name__ == "__main__":
    main()
