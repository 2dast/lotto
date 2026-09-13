"""scripts/report_template.html을 바탕으로 data/draws.json 최신 분석 결과와
predictions/의 최신 추천 번호를 채워 reports/lotto_report_<타임스탬프>.html로 저장한다.
매 실행마다 새 파일을 남겨 이력으로 쌓이며, 템플릿 자체는 건드리지 않는다.
"""
import datetime as dt
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "draws.json"
TEMPLATE_PATH = ROOT / "scripts" / "report_template.html"
PREDICTIONS_DIR = ROOT / "predictions"
REPORT_DIR = ROOT / "reports"

ZONES = [(1, 9), (10, 19), (20, 29), (30, 39), (40, 45)]
ALL_NUMBERS = list(range(1, 46))
KST = dt.timezone(dt.timedelta(hours=9))
WINDOW = 50
SIMULATIONS_PER_DRAW = 20


def odd_count(numbers):
    return sum(1 for n in numbers if n % 2 == 1)


def max_consecutive(numbers):
    s = sorted(numbers)
    max_run = cur_run = 1
    for a, b in zip(s, s[1:]):
        if b == a + 1:
            cur_run += 1
            max_run = max(max_run, cur_run)
        else:
            cur_run = 1
    return max_run


def zone_counts(numbers):
    return [sum(1 for n in numbers if lo <= n <= hi) for lo, hi in ZONES]


def compute_pattern_stats(draws):
    numbers_list = [d["numbers"] for d in draws]
    odd_counts = [odd_count(n) for n in numbers_list]
    sums = [sum(n) for n in numbers_list]
    max_runs = [max_consecutive(n) for n in numbers_list]
    zones_per_draw = [zone_counts(n) for n in numbers_list]

    odd_dist = [odd_counts.count(k) for k in range(7)]
    max_run_cap = max(max_runs) if max_runs else 1
    run_dist = [max_runs.count(k) for k in range(1, max_run_cap + 1)]

    sum_bins = list(range(40, 250, 10))
    sum_hist = [0] * len(sum_bins)
    for s in sums:
        idx = min(max((s - 40) // 10, 0), len(sum_bins) - 1)
        sum_hist[idx] += 1

    zone_avgs = []
    for i in range(5):
        col = [z[i] for z in zones_per_draw]
        zone_avgs.append(sum(col) / len(col))

    all_freq = {n: 0 for n in ALL_NUMBERS}
    for n in numbers_list:
        for x in n:
            all_freq[x] += 1

    return {
        "odd_dist": odd_dist,
        "sum_bins": sum_bins,
        "sum_hist": sum_hist,
        "sum_avg": sum(sums) / len(sums),
        "run_dist": run_dist,
        "zone_labels": ["1-9", "10-19", "20-29", "30-39", "40-45"],
        "zone_avgs": zone_avgs,
        "all_freq": [all_freq[n] for n in ALL_NUMBERS],
    }


def recent_freq(draws, end_idx, window):
    count = {n: 0 for n in ALL_NUMBERS}
    for d in draws[max(0, end_idx - window):end_idx]:
        for n in d["numbers"]:
            count[n] += 1
    return count


def strategy_weights(freq, mode):
    if mode == "neutral":
        return {n: 1.0 for n in ALL_NUMBERS}
    max_f = max(freq.values()) or 1
    if mode == "hot":
        return {n: freq[n] / max_f for n in ALL_NUMBERS}
    return {n: 1.0 - freq[n] / max_f for n in ALL_NUMBERS}  # cold


def weighted_pick(weights, k=6):
    pool = list(ALL_NUMBERS)
    picked = []
    for _ in range(k):
        w = [weights[n] + 0.01 for n in pool]
        chosen = random.choices(pool, weights=w, k=1)[0]
        picked.append(chosen)
        pool.remove(chosen)
    return set(picked)


def compute_backtest(draws):
    modes = ["hot", "cold", "neutral"]
    totals = {m: 0 for m in modes}
    trials = {m: 0 for m in modes}

    for idx in range(WINDOW, len(draws)):
        actual = set(draws[idx]["numbers"])
        freq = recent_freq(draws, idx, WINDOW)
        for mode in modes:
            weights = strategy_weights(freq, mode)
            for _ in range(SIMULATIONS_PER_DRAW):
                picked = weighted_pick(weights)
                totals[mode] += len(picked & actual)
                trials[mode] += 1

    result = {m: totals[m] / trials[m] for m in modes}
    result["random"] = 6 * 6 / 45
    return result


def set_span(html: str, span_id: str, value: str) -> str:
    pattern = re.compile(rf'(id="{span_id}">)[^<]*(<)')
    new_html, n = pattern.subn(rf"\g<1>{value}\g<2>", html)
    if n == 0:
        raise ValueError(f"id={span_id!r} 스팬을 리포트에서 찾을 수 없습니다")
    return new_html


def load_latest_predictions() -> dict:
    files = sorted(PREDICTIONS_DIR.glob("predictions_*.json"))
    if not files:
        raise FileNotFoundError("predictions/predictions_*.json이 없습니다. scripts/predict.py를 먼저 실행하세요")
    latest = files[-1]
    return latest.name, json.loads(latest.read_text(encoding="utf-8"))


def main() -> None:
    draws = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    stats = compute_pattern_stats(draws)
    backtest = compute_backtest(draws)
    pred_filename, pred_data = load_latest_predictions()

    data_obj = {
        "odd_dist": stats["odd_dist"],
        "sum_bins": stats["sum_bins"],
        "sum_hist": stats["sum_hist"],
        "run_dist": stats["run_dist"],
        "zone_labels": stats["zone_labels"],
        "zone_avgs": [round(v, 4) for v in stats["zone_avgs"]],
        "all_freq": stats["all_freq"],
        "backtest": {k: round(v, 4) for k, v in backtest.items()},
        "predictions": pred_data["predictions"],
    }

    html = TEMPLATE_PATH.read_text(encoding="utf-8")
    html = re.sub(
        r"const DATA = \{.*?\};",
        "const DATA = " + json.dumps(data_obj, ensure_ascii=False) + ";",
        html,
        count=1,
        flags=re.DOTALL,
    )

    total = len(draws)
    first_date = draws[0]["date"]
    last_date = draws[-1]["date"]
    based_on = pred_data["based_on_drwNo"]
    today = dt.datetime.now(KST).strftime("%Y.%m.%d")

    html = set_span(html, "f-date", today)
    html = set_span(html, "f-total", str(total))
    html = set_span(html, "f-total2", str(total))
    html = set_span(html, "f-daterange", f"{first_date} ~ {last_date}")
    html = set_span(html, "f-count", f"{total:,}")
    html = set_span(html, "f-avgsum", f"{stats['sum_avg']:.1f}")
    html = set_span(html, "f-hot", f"{backtest['hot']:.4f}")
    html = set_span(html, "f-random", f"{backtest['random']:.4f}")
    html = set_span(html, "f-simrange", f"{total - WINDOW}회차({WINDOW + 1}~{total})")
    html = set_span(html, "f-basedon", str(based_on))
    html = set_span(html, "f-basedon2", str(based_on + 1))
    html = set_span(html, "f-predfile", pred_filename)

    # predictions_<ts>.json 의 타임스탬프를 그대로 리포트 파일명에 붙여 1:1로 이력 관리
    ts = pred_filename.removeprefix("predictions_").removesuffix(".json")
    REPORT_DIR.mkdir(exist_ok=True)
    report_path = REPORT_DIR / f"lotto_report_{ts}.html"
    report_path.write_text(html, encoding="utf-8")
    print(f"리포트 생성됨 -> {report_path} (총 {total}회차, 기준회차 {based_on})")


if __name__ == "__main__":
    main()
