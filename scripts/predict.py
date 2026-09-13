"""RULES.md의 조건과 data/draws.json 기반으로 예측 번호 세트를 생성한다."""
import datetime as dt
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULES_PATH = ROOT / "RULES.md"
DATA_PATH = ROOT / "data" / "draws.json"
OUTPUT_DIR = ROOT / "predictions"

ALL_NUMBERS = list(range(1, 46))
KST = dt.timezone(dt.timedelta(hours=9))

DEFAULT_ZONES = [(1, 9), (10, 19), (20, 29), (30, 39), (40, 45)]


def _parse_rule_lines(lines: list[str]) -> dict:
    zones = []
    rules = {
        "frequency": {"all_time_weight": 0.5, "recent_weight": 0.5, "recent_window": 20},
        "pattern_filters": {
            "odd_even_ratio": [0, 6],
            "max_consecutive": 6,
            "sum_range": [21, 255],
            "zones": [],
        },
        "num_predictions": 5,
        "exclude_numbers": [],
        "include_numbers": [],
    }

    for raw_line in lines:
        line = raw_line.split("#", 1)[0].strip()  # 줄 끝 한글 설명(#...)은 무시
        if not line:
            continue
        tokens = line.split()
        keyword = tokens[0]

        if keyword == "odd_even":
            rules["pattern_filters"]["odd_even_ratio"] = [int(tokens[1]), int(tokens[2])]
        elif keyword == "sum":
            rules["pattern_filters"]["sum_range"] = [int(tokens[1]), int(tokens[2])]
        elif keyword == "consecutive_max":
            rules["pattern_filters"]["max_consecutive"] = int(tokens[1])
        elif keyword == "zone":
            # zone <start> <end> min <n> max <n>
            zones.append({
                "range": [int(tokens[1]), int(tokens[2])],
                "min": int(tokens[4]),
                "max": int(tokens[6]),
            })
        elif keyword == "predictions":
            rules["num_predictions"] = int(tokens[1])
        elif keyword == "freq_all_weight":
            rules["frequency"]["all_time_weight"] = float(tokens[1])
        elif keyword == "freq_recent_weight":
            rules["frequency"]["recent_weight"] = float(tokens[1])
        elif keyword == "freq_recent_window":
            rules["frequency"]["recent_window"] = int(tokens[1])
        elif keyword == "exclude":
            rules["exclude_numbers"].extend(int(t) for t in tokens[1:])
        elif keyword == "include":
            rules["include_numbers"].extend(int(t) for t in tokens[1:])
        else:
            raise ValueError(f"알 수 없는 조건 키워드: {keyword!r} (줄: {raw_line!r})")

    if zones:
        rules["pattern_filters"]["zones"] = zones
    return rules


def load_rules(path: Path = RULES_PATH) -> dict:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"```\n(.*?)```", text, re.DOTALL)
    if not match:
        raise ValueError("RULES.md에서 조건 코드블록을 찾을 수 없습니다")
    return _parse_rule_lines(match.group(1).splitlines())


def load_draws(path: Path = DATA_PATH) -> list[dict]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def score_numbers(draws: list[dict], rules: dict) -> dict[int, float]:
    freq_cfg = rules["frequency"]
    all_time_weight = freq_cfg["all_time_weight"]
    recent_weight = freq_cfg["recent_weight"]
    recent_window = freq_cfg["recent_window"]

    all_time_count = {n: 0 for n in ALL_NUMBERS}
    recent_count = {n: 0 for n in ALL_NUMBERS}

    for draw in draws:
        for n in draw["numbers"]:
            all_time_count[n] += 1

    for draw in draws[-recent_window:]:
        for n in draw["numbers"]:
            recent_count[n] += 1

    max_all = max(all_time_count.values(), default=0) or 1
    max_recent = max(recent_count.values(), default=0) or 1

    return {
        n: all_time_weight * (all_time_count[n] / max_all)
        + recent_weight * (recent_count[n] / max_recent)
        for n in ALL_NUMBERS
    }


def passes_filters(combo: list[int], filters: dict) -> bool:
    odd_count = sum(1 for n in combo if n % 2 == 1)
    lo, hi = filters["odd_even_ratio"]
    if not (lo <= odd_count <= hi):
        return False

    if not (filters["sum_range"][0] <= sum(combo) <= filters["sum_range"][1]):
        return False

    sorted_combo = sorted(combo)
    max_run = 1
    cur_run = 1
    for a, b in zip(sorted_combo, sorted_combo[1:]):
        if b == a + 1:
            cur_run += 1
            max_run = max(max_run, cur_run)
        else:
            cur_run = 1
    if max_run > filters["max_consecutive"]:
        return False

    for zone in filters["zones"]:
        lo_z, hi_z = zone["range"]
        count = sum(1 for n in combo if lo_z <= n <= hi_z)
        if not (zone["min"] <= count <= zone["max"]):
            return False

    return True


def weighted_sample(candidates: list[int], scores: dict[int, float], k: int) -> list[int]:
    pool = list(candidates)
    picked = []
    for _ in range(k):
        weights = [scores[n] + 0.01 for n in pool]  # 0점 번호도 뽑힐 여지를 남김
        chosen = random.choices(pool, weights=weights, k=1)[0]
        picked.append(chosen)
        pool.remove(chosen)
    return picked


def generate_combo(pool: list[int], scores: dict[int, float], filters: dict,
                    exclude: set, include: set, max_attempts: int = 2000) -> list[int] | None:
    candidates = [n for n in pool if n not in exclude]
    for _ in range(max_attempts):
        combo = set(include)
        remaining = [n for n in candidates if n not in combo]
        combo.update(weighted_sample(remaining, scores, 6 - len(combo)))
        combo = sorted(combo)
        if passes_filters(combo, filters):
            return combo
    return None


def generate_predictions(rules: dict, scores: dict[int, float]) -> list[list[int]]:
    filters = rules["pattern_filters"]
    exclude = set(rules.get("exclude_numbers") or [])
    include = set(rules.get("include_numbers") or [])
    num_predictions = rules["num_predictions"]

    pool = [n for n in ALL_NUMBERS if n not in exclude]

    predictions = []
    seen = set()
    attempts = 0
    while len(predictions) < num_predictions and attempts < num_predictions * 500:
        attempts += 1
        combo = generate_combo(pool, scores, filters, exclude, include)
        if combo is None:
            continue
        key = tuple(combo)
        if key in seen:
            continue
        seen.add(key)
        predictions.append(combo)
    return predictions


def main() -> None:
    rules = load_rules()
    draws = load_draws()
    scores = score_numbers(draws, rules)
    predictions = generate_predictions(rules, scores)

    last_drw_no = max((d["drwNo"] for d in draws), default=0)
    now = dt.datetime.now(KST)
    output = {
        "based_on_drwNo": last_drw_no,
        "generated_at": now.isoformat(timespec="seconds"),
        "predictions": predictions,
    }

    OUTPUT_DIR.mkdir(exist_ok=True)
    output_path = OUTPUT_DIR / f"predictions_{now.strftime('%Y%m%d_%H%M%S')}.json"
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(predictions)}개 세트 생성됨 -> {output_path}")


if __name__ == "__main__":
    main()
