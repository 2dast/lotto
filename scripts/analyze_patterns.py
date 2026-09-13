"""과거 당첨 조합들의 실제 패턴 분포(홀짝비/합계/구간분포/최대연속개수)를 집계해
RULES.md의 필터 값들이 실제 분포와 맞는지 확인한다. RULES.md/predict.py는 수정하지 않는다.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "draws.json"

ZONES = [(1, 9), (10, 19), (20, 29), (30, 39), (40, 45)]


def load_draws(path: Path = DATA_PATH) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def odd_count(numbers: list[int]) -> int:
    return sum(1 for n in numbers if n % 2 == 1)


def max_consecutive(numbers: list[int]) -> int:
    s = sorted(numbers)
    max_run = cur_run = 1
    for a, b in zip(s, s[1:]):
        if b == a + 1:
            cur_run += 1
            max_run = max(max_run, cur_run)
        else:
            cur_run = 1
    return max_run


def zone_counts(numbers: list[int]) -> list[int]:
    return [sum(1 for n in numbers if lo <= n <= hi) for lo, hi in ZONES]


def percentile(values: list[int], p: float) -> float:
    s = sorted(values)
    idx = int(round((len(s) - 1) * p))
    return s[idx]


def main() -> None:
    draws = load_draws()
    numbers_list = [d["numbers"] for d in draws]

    odd_counts = [odd_count(n) for n in numbers_list]
    sums = [sum(n) for n in numbers_list]
    max_runs = [max_consecutive(n) for n in numbers_list]
    zones_per_draw = [zone_counts(n) for n in numbers_list]

    print(f"분석 대상: 전체 {len(draws)}회차\n")

    print("[홀수 개수 분포 (0~6)]")
    for k in range(7):
        cnt = odd_counts.count(k)
        print(f"  홀수 {k}개: {cnt}회 ({cnt / len(draws) * 100:.1f}%)")
    print(f"  -> 5~95 percentile: {percentile(odd_counts, 0.05):.0f} ~ {percentile(odd_counts, 0.95):.0f}\n")

    print("[합계 분포]")
    print(f"  최소 {min(sums)}, 최대 {max(sums)}, 평균 {sum(sums) / len(sums):.1f}")
    print(f"  -> 5~95 percentile: {percentile(sums, 0.05):.0f} ~ {percentile(sums, 0.95):.0f}\n")

    print("[최대 연속번호 개수 분포]")
    for k in range(1, max(max_runs) + 1):
        cnt = max_runs.count(k)
        if cnt:
            print(f"  연속 {k}개: {cnt}회 ({cnt / len(draws) * 100:.1f}%)")
    print(f"  -> 95 percentile: {percentile(max_runs, 0.95):.0f}\n")

    print("[구간별 평균 개수 / 5~95 percentile]")
    for i, (lo, hi) in enumerate(ZONES):
        col = [z[i] for z in zones_per_draw]
        avg = sum(col) / len(col)
        print(f"  {lo:>2}-{hi:<2}: 평균 {avg:.2f}개, 5~95pct {percentile(col, 0.05):.0f}~{percentile(col, 0.95):.0f}")

    print("\n[RULES.md 현재 값과 비교]")
    print("  odd_even 2 4  vs  실제 5~95pct 위 참고")
    print("  sum 100 170   vs  실제 5~95pct 위 참고")
    print("  consecutive_max 2  vs  실제 95pct 위 참고")
    print("  zone ... min 0 max 3 (1~39), min 1 max 1 (40~45)  vs  실제 구간별 분포 위 참고")


if __name__ == "__main__":
    main()
