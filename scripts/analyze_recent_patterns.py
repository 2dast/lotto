"""최근 N회차의 번호 패턴이 전체 기간 통계와 실제로 다른지 비교한다.

사용자가 최근 회차에서 육안으로 관찰한 패턴(예: "40~45 구간 숫자가 거의
항상 1개는 포함된다")이 통계적으로 유의미한 추세인지, 아니면 표본이
작아서 생긴 착시인지 판단할 근거를 콘솔에 출력한다. RULES.md는 건드리지
않는다 — 이 스크립트는 순수 분석/리포트 용도다.
"""
import argparse
import statistics
import sys
from pathlib import Path

from predict import DEFAULT_ZONES, load_draws

ROOT = Path(__file__).resolve().parent.parent


def zone_label(zone: tuple[int, int]) -> str:
    lo, hi = zone
    return f"{lo}~{hi}"


def zone_count(combo: list[int], zone: tuple[int, int]) -> int:
    lo, hi = zone
    return sum(1 for n in combo if lo <= n <= hi)


def odd_count(combo: list[int]) -> int:
    return sum(1 for n in combo if n % 2 == 1)


def max_consecutive(combo: list[int]) -> int:
    sorted_combo = sorted(combo)
    max_run = 1
    cur_run = 1
    for a, b in zip(sorted_combo, sorted_combo[1:]):
        if b == a + 1:
            cur_run += 1
            max_run = max(max_run, cur_run)
        else:
            cur_run = 1
    return max_run


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    return statistics.quantiles(values, n=100, method="inclusive")[int(pct) - 1] if len(values) > 1 else values[0]


def zone_stats(draws: list[dict], zones: list[tuple[int, int]]) -> dict[str, dict]:
    counts = {zone_label(z): [] for z in zones}
    for d in draws:
        for z in zones:
            counts[zone_label(z)].append(zone_count(d["numbers"], z))

    stats = {}
    for label, values in counts.items():
        zero_pct = 100 * sum(1 for v in values if v == 0) / len(values) if values else 0.0
        one_plus_pct = 100 - zero_pct
        stats[label] = {
            "avg": statistics.mean(values) if values else 0.0,
            "median": statistics.median(values) if values else 0.0,
            "min": min(values, default=0),
            "max": max(values, default=0),
            "zero_pct": zero_pct,
            "one_plus_pct": one_plus_pct,
        }
    return stats


def general_stats(draws: list[dict]) -> dict:
    odds = [odd_count(d["numbers"]) for d in draws]
    sums = [sum(d["numbers"]) for d in draws]
    consecutives = [max_consecutive(d["numbers"]) for d in draws]
    return {
        "odd_avg": statistics.mean(odds) if odds else 0.0,
        "sum_avg": statistics.mean(sums) if sums else 0.0,
        "sum_p5": percentile(sums, 5),
        "sum_p95": percentile(sums, 95),
        "consecutive_avg": statistics.mean(consecutives) if consecutives else 0.0,
        "consecutive_p95": percentile(consecutives, 95),
    }


def print_report(draws: list[dict], window: int) -> None:
    recent = draws[-window:]
    zones = DEFAULT_ZONES

    print(f"=== 최근 {len(recent)}회차 vs 전체 {len(draws)}회차 패턴 비교 ===\n")

    recent_zone = zone_stats(recent, zones)
    all_zone = zone_stats(draws, zones)

    print(f"{'구간':<8} {'최근 평균':>10} {'최근 0개%':>10} {'전체 평균':>10} {'전체 0개%':>10}")
    for z in zones:
        label = zone_label(z)
        r, a = recent_zone[label], all_zone[label]
        print(f"{label:<8} {r['avg']:>10.2f} {r['zero_pct']:>9.1f}% {a['avg']:>10.2f} {a['zero_pct']:>9.1f}%")

    print()
    last_zone = zone_label(zones[-1])
    r_last = recent_zone[last_zone]
    a_last = all_zone[last_zone]
    print(
        f"[{last_zone} 구간] 최근 {len(recent)}회차 중 0개인 회차: "
        f"{round(r_last['zero_pct'] / 100 * len(recent))}회 ({r_last['zero_pct']:.1f}%) · "
        f"전체 {len(draws)}회차 기준 0개 비율: {a_last['zero_pct']:.1f}%"
    )
    diff = a_last["zero_pct"] - r_last["zero_pct"]
    if abs(diff) < 5:
        print(f"  → 최근과 전체의 차이가 {abs(diff):.1f}%p로 크지 않음 — 표본이 작아 생긴 우연일 가능성이 높음.")
    else:
        print(f"  → 최근과 전체 차이가 {abs(diff):.1f}%p — 단순 우연이라기엔 차이가 있어 보임 (표본 20개는 여전히 작으니 주의).")

    print()
    r_gen = general_stats(recent)
    a_gen = general_stats(draws)
    print(f"{'지표':<14} {'최근':>10} {'전체':>10}")
    print(f"{'홀수 평균개수':<14} {r_gen['odd_avg']:>10.2f} {a_gen['odd_avg']:>10.2f}")
    print(f"{'합계 평균':<14} {r_gen['sum_avg']:>10.1f} {a_gen['sum_avg']:>10.1f}")
    print(f"{'합계 5~95pct':<14} {r_gen['sum_p5']:>4.0f}~{r_gen['sum_p95']:<5.0f} {a_gen['sum_p5']:>4.0f}~{a_gen['sum_p95']:<5.0f}")
    print(f"{'연속 최대 평균':<14} {r_gen['consecutive_avg']:>10.2f} {a_gen['consecutive_avg']:>10.2f}")
    print(f"{'연속 최대 95pct':<14} {r_gen['consecutive_p95']:>10.1f} {a_gen['consecutive_p95']:>10.1f}")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # Windows 콘솔 cp949 깨짐 방지
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--window", type=int, default=20, help="'최근'으로 볼 회차 수 (기본 20)")
    args = parser.parse_args()

    draws = load_draws()
    if not draws:
        print("data/draws.json이 비어있습니다.")
        return
    print_report(draws, args.window)


if __name__ == "__main__":
    main()
