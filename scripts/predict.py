"""RULES.md의 조건과 data/draws.json 기반으로 예측 번호 세트를 생성한다."""
import datetime as dt
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULES_PATH = ROOT / "RULES.md"
RULES_2_PATH = ROOT / "RULES_2.md"
DATA_PATH = ROOT / "data" / "draws.json"
OUTPUT_DIR = ROOT / "predictions"

ALL_NUMBERS = list(range(1, 46))
KST = dt.timezone(dt.timedelta(hours=9))

DEFAULT_ZONES = [(1, 9), (10, 19), (20, 29), (30, 39), (40, 45)]


def _parse_rule_lines(lines: list[str]) -> dict:
    zones = []
    rules = {
        "frequency": {"all_time_weight": 0.5, "recent_weight": 0.5, "recent_window": 20, "mode": "hot"},
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
        elif keyword == "freq_mode":
            if tokens[1] not in ("hot", "cold"):
                raise ValueError(f"freq_mode는 hot/cold만 허용: {tokens[1]!r}")
            rules["frequency"]["mode"] = tokens[1]
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
    mode = freq_cfg.get("mode", "hot")

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

    all_time_norm = {n: all_time_count[n] / max_all for n in ALL_NUMBERS}
    recent_norm = {n: recent_count[n] / max_recent for n in ALL_NUMBERS}

    if mode == "cold":
        # "많이 나온 번호"가 아니라 "적게 나온 번호"를 우대 (1안과 반대 방향 베팅)
        all_time_norm = {n: 1 - v for n, v in all_time_norm.items()}
        recent_norm = {n: 1 - v for n, v in recent_norm.items()}

    return {
        n: all_time_weight * all_time_norm[n] + recent_weight * recent_norm[n]
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


def generate_option(rules_path: Path, draws: list[dict]) -> list[list[int]] | None:
    """rules_path가 없으면 None(해당 안은 이번 회차에 생성하지 않음)."""
    if not rules_path.exists():
        return None
    rules = load_rules(rules_path)
    scores = score_numbers(draws, rules)
    return generate_predictions(rules, scores)


def main() -> None:
    draws = load_draws()
    option1 = generate_option(RULES_PATH, draws)
    if option1 is None:
        raise FileNotFoundError(f"{RULES_PATH} 파일이 없습니다")
    option2 = generate_option(RULES_2_PATH, draws)

    last_drw_no = max((d["drwNo"] for d in draws), default=0)
    now = dt.datetime.now(KST)
    output = {
        "based_on_drwNo": last_drw_no,
        "generated_at": now.isoformat(timespec="seconds"),
        "option1": {"predictions": option1},
        "option2": {"predictions": option2} if option2 is not None else None,
    }

    next_draw = last_drw_no + 1
    round_dir = OUTPUT_DIR / f"round_{next_draw}"
    round_dir.mkdir(parents=True, exist_ok=True)
    output_path = round_dir / f"predictions_{next_draw}_{now.strftime('%Y%m%d_%H%M%S')}.json"
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    option2_note = f", 2안 {len(option2)}개" if option2 is not None else " (2안 없음)"
    print(f"1안 {len(option1)}개{option2_note} 세트 생성됨 -> {output_path}")


if __name__ == "__main__":
    main()
