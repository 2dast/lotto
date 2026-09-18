"""저장소 루트에 index.html 대시보드를 생성한다. 메인 화면은 최신 실제 당첨번호와
다음 회차 예측 5세트를 보여주고, 왼쪽 사이드바에서 회차별 리포트를
선택하면 같은 화면 안에서 그 리포트(reports/lotto_report_<ts>.html)를 바로 보여준다.
(reports/ 안의 회차 그룹핑은 build_index.list_reports를 그대로 재사용한다.)

화면 톤은 design.md(토스 디자인 시스템 토큰 기반)를 따른다.
"""
import datetime as dt
import itertools
import json
from pathlib import Path

from build_index import list_reports

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "draws.json"
PREDICTIONS_DIR = ROOT / "predictions"
OUTPUT_PATH = ROOT / "index.html"
KST = dt.timezone(dt.timedelta(hours=9))

BALL_COLORS = ["ball-yellow", "ball-blue", "ball-red", "ball-grey", "ball-green"]


def ball_zone(n: int) -> str:
    return BALL_COLORS[min((n - 1) // 10, 4)]


def number_ball(n: int, hit: bool = False) -> str:
    cls = f"number-ball {ball_zone(n)}" + (" hit" if hit else "")
    return f'<span class="{cls}">{n}</span>'


def option1_predictions(data: dict) -> list[list[int]]:
    """predict.py가 예전엔 {"predictions": [...]} 형태(1안만)로 저장했다 — 그 시절 파일도 계속 읽을 수 있게 둘 다 지원."""
    if "option1" in data:
        return data["option1"]["predictions"]
    return data["predictions"]


def option2_predictions(data: dict) -> list[list[int]] | None:
    """2안이 없던 시절 파일, 혹은 2안 생성이 스킵된 회차는 None."""
    option2 = data.get("option2")
    return option2["predictions"] if option2 else None


def load_latest_predictions() -> tuple[str, dict]:
    files = list(PREDICTIONS_DIR.glob("round_*/predictions_*.json"))
    # 파일명의 회차 번호가 zero-padding 없이 들어가 이름순 정렬은 신뢰할 수 없다.
    # generated_at(ISO8601) 값으로 정렬해 진짜 최신 파일을 고른다.
    candidates = [(json.loads(p.read_text(encoding="utf-8")), p) for p in files]
    data, latest = max(candidates, key=lambda c: c[0]["generated_at"])
    return latest.name, data


def load_all_predictions() -> list[dict]:
    """predictions/ 안의 모든 예측 파일을 회차 선택 드롭다운용으로 모은다. (대시보드는 1안만 보여준다)"""
    entries = []
    for path in sorted(PREDICTIONS_DIR.glob("round_*/predictions_*.json"), key=lambda p: p.name):
        data = json.loads(path.read_text(encoding="utf-8"))
        entries.append({
            "file": path.name,
            "based_on_drwNo": data["based_on_drwNo"],
            "next_draw": data["based_on_drwNo"] + 1,
            "generated_at": data["generated_at"],
            "predictions": option1_predictions(data),
            "option2": option2_predictions(data),
        })
    entries.sort(key=lambda e: e["generated_at"], reverse=True)
    return entries


def next_draw_date_label(latest_draw: dict) -> str:
    """로또는 매주 토요일 추첨이므로 마지막 실제 회차 날짜 + 7일 = 다음 추첨일."""
    last_date = dt.datetime.strptime(latest_draw["date"], "%Y-%m-%d").date()
    next_date = last_date + dt.timedelta(days=7)
    today = dt.datetime.now(KST).date()
    d_day = (next_date - today).days
    if d_day > 0:
        return f"다음 추첨 {next_date.isoformat()} (D-{d_day})"
    if d_day == 0:
        return f"다음 추첨 {next_date.isoformat()} (오늘)"
    return f"다음 추첨 {next_date.isoformat()} (결과 반영 대기)"


def recent_draws_rows(draws: list[dict], n: int = 5) -> str:
    rows = []
    for d in reversed(draws[-n:]):
        balls = " ".join(number_ball(x) for x in d["numbers"])
        amount = d.get("firstPrizeAmount")
        amount_label = f'{amount:,}원' if amount is not None else "정보 없음"
        rows.append(f"""          <li class="recent-row">
            <div class="recent-line">
              <span class="recent-no table-numeric">{d["drwNo"]}회</span>
              <span class="recent-balls">{balls}</span>
            </div>
            <div class="recent-line">
              <span class="recent-date table-numeric">{d["date"]}</span>
              <span class="recent-amount table-numeric">1등 {amount_label}</span>
            </div>
          </li>""")
    return "\n".join(rows)


def render_summary(
    draws: list[dict],
    latest_draw: dict,
    pred_filename: str,
    pred_data: dict,
    all_predictions: list[dict],
    dday_label: str,
    generated_at_label: str,
) -> tuple[str, str]:
    """대시보드 메인 화면(최신 당첨 + 예측)의 HTML과 <script>를 반환한다.

    적중 이력은 별도 파일에 미리 계산해두지 않고, 선택된 예측 파일과 실제 당첨번호를
    그 자리에서 비교해 클라이언트에서 계산한다 — 같은 회차에 예측 파일이 여러 개
    있어도(재실행 등) 고른 파일 기준으로 항상 정확한 적중 결과를 보여준다.
    """
    based_on = pred_data["based_on_drwNo"]
    next_draw = based_on + 1
    recent_rows = recent_draws_rows(draws)

    rounds = sorted({e["next_draw"] for e in all_predictions}, reverse=True)
    round_options = "\n".join(
        f'          <option value="{r}"{" selected" if r == next_draw else ""}>{r}회차</option>'
        for r in rounds
    )

    predictions_json = json.dumps(all_predictions, ensure_ascii=False)
    draws_by_no_json = json.dumps({d["drwNo"]: d["numbers"] for d in draws}, ensure_ascii=False)

    shared_script = f"""
    const PREDICTIONS = {predictions_json};
    const DRAWS_BY_NO = {draws_by_no_json};
    const BALL_COLORS = ["ball-yellow", "ball-blue", "ball-red", "ball-grey", "ball-green"];

    function ballHtml(n, hit) {{
      const zone = BALL_COLORS[Math.min(Math.floor((n - 1) / 10), 4)];
      return `<span class="number-ball ${{zone}}${{hit ? ' hit' : ''}}">${{n}}</span>`;
    }}
    function computeHits(predictions, actualNumbers) {{
      const actual = new Set(actualNumbers);
      return predictions.map(combo => combo.filter(n => actual.has(n)).length);
    }}

    const roundSelect = document.getElementById('round-select');
    const fileSelect = document.getElementById('file-select');
    const predList = document.getElementById('pred-list');
    const predSummary = document.getElementById('pred-summary');
    const predTitle = document.getElementById('pred-title');

    function filesForRound(round) {{
      return PREDICTIONS.filter(p => p.next_draw === Number(round));
    }}

    function renderFileOptions(round) {{
      const files = filesForRound(round);
      fileSelect.innerHTML = files.map(f =>
        `<option value="${{f.file}}">${{f.generated_at.replace('T', ' ').slice(0, 16)}}</option>`
      ).join('');
    }}

    const pred2Card = document.getElementById('pred2-card');
    const pred2List = document.getElementById('pred2-list');
    const pred2Summary = document.getElementById('pred2-summary');
    const pred2Title = document.getElementById('pred2-title');

    function renderPredList(listEl, predictions, actualNumbers) {{
      if (actualNumbers) {{
        const hitSet = new Set(actualNumbers);
        listEl.innerHTML = predictions.map((combo, i) => `
          <li class="pred-row">
            <span class="set-idx">${{i + 1}}</span>
            <span class="set-nums">${{combo.map(n => ballHtml(n, hitSet.has(n))).join(' ')}}</span>
          </li>
        `).join('');
      }} else {{
        listEl.innerHTML = predictions.map((combo, i) => `
          <li class="pred-row">
            <span class="set-idx">${{i + 1}}</span>
            <span class="set-nums">${{combo.map(n => ballHtml(n, false)).join(' ')}}</span>
          </li>
        `).join('');
      }}
    }}

    function renderPrediction(round, filename) {{
      const entry = PREDICTIONS.find(p => p.next_draw === Number(round) && p.file === filename);
      if (!entry) return;
      predTitle.textContent = `${{entry.next_draw}}회차 예측 (1안)`;

      const actualNumbers = DRAWS_BY_NO[entry.next_draw];
      if (actualNumbers) {{
        const hits = computeHits(entry.predictions, actualNumbers);
        const best = Math.max(...hits);
        const badges = hits.map(h => `<span class="accuracy-badge${{h === 0 ? ' dim' : ''}}">${{h}}개</span>`).join(' ');
        predSummary.innerHTML = `적중 ${{badges}} · 최고 ${{best}}개`;
      }} else {{
        predSummary.textContent = '아직 추첨 전입니다 — 결과 발표 후 적중 이력이 집계됩니다.';
      }}
      renderPredList(predList, entry.predictions, actualNumbers);

      if (entry.option2) {{
        pred2Card.hidden = false;
        pred2Title.textContent = `${{entry.next_draw}}회차 예측 (2안)`;
        if (actualNumbers) {{
          const hits2 = computeHits(entry.option2, actualNumbers);
          const best2 = Math.max(...hits2);
          const badges2 = hits2.map(h => `<span class="accuracy-badge${{h === 0 ? ' dim' : ''}}">${{h}}개</span>`).join(' ');
          pred2Summary.innerHTML = `적중 ${{badges2}} · 최고 ${{best2}}개`;
        }} else {{
          pred2Summary.textContent = '아직 추첨 전입니다 — 결과 발표 후 적중 이력이 집계됩니다.';
        }}
        renderPredList(pred2List, entry.option2, actualNumbers);
      }} else {{
        pred2Card.hidden = true;
      }}
    }}

    roundSelect.addEventListener('change', () => {{
      renderFileOptions(roundSelect.value);
      renderPrediction(roundSelect.value, fileSelect.value);
    }});
    fileSelect.addEventListener('change', () => {{
      renderPrediction(roundSelect.value, fileSelect.value);
    }});

    renderFileOptions(roundSelect.value);
    fileSelect.value = "{pred_filename}";
    renderPrediction(roundSelect.value, fileSelect.value);
"""

    html = f"""
      <section class="card">
        <div class="pred-header">
          <h2 class="h3" id="pred-title">{next_draw}회차 예측</h2>
          <div class="select-row">
            <select id="round-select" aria-label="예측 회차 선택">
{round_options}
            </select>
            <select id="file-select" aria-label="예측 파일 선택"></select>
          </div>
        </div>
        <p class="body-1" id="pred-summary" style="margin:0 0 10px"></p>
        <ul class="pred-list" id="pred-list"></ul>
      </section>

      <section class="card" id="pred2-card" hidden>
        <h2 class="h3" id="pred2-title">2안 예측</h2>
        <p class="body-1" id="pred2-summary" style="margin:0 0 10px"></p>
        <ul class="pred-list" id="pred2-list"></ul>
      </section>

      <section class="card">
        <h2 class="h3">최근 5회차 당첨결과</h2>
        <ul class="recent-list">
{recent_rows}
        </ul>
        <p class="caption">{dday_label}</p>
      </section>

      <div class="dash-footer">
        <p class="footnote">본 예측은 통계적 근거가 없으며 오락 목적입니다. 로또는 완전 무작위 추첨입니다.</p>
        <p class="footnote">마지막 갱신: {generated_at_label} (KST, GitHub Actions 자동 실행)</p>
      </div>"""
    return html, shared_script


def render_sidebar(reports: list[tuple[int, object, str]]) -> str:
    """reports/index.html과 동일한 회차별 아코디언 목록을 사이드바에 그대로 재사용한다."""
    if not reports:
        return '<p class="caption" style="padding:8px 16px">아직 생성된 리포트가 없습니다.</p>'

    groups = []
    for next_draw, group in itertools.groupby(reports, key=lambda r: r[0]):
        groups.append((next_draw, list(group)))

    sections = []
    for gi, (next_draw, group) in enumerate(groups):
        hidden_group = gi >= 10
        items = "\n".join(
            f'            <li><a href="#" data-src="reports/{name}">'
            f'{ts.strftime("%Y-%m-%d %H:%M")}</a></li>'
            for _, ts, name in group
        )
        sections.append(f"""        <li class="draw-group{' is-hidden' if hidden_group else ''}">
          <button class="draw-header" type="button" aria-expanded="false">
            <span class="chevron">&#9656;</span>
            <span class="draw-label">{next_draw}회차 예측</span>
            <span class="draw-count">{len(group)}</span>
          </button>
          <ul class="draw-body">
{items}
          </ul>
        </li>""")
    return "\n".join(sections)


def main() -> None:
    draws = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    latest_draw = draws[-1]
    pred_filename, pred_data = load_latest_predictions()
    reports = list_reports()
    all_predictions = load_all_predictions()
    dday_label = next_draw_date_label(latest_draw)
    generated_at_label = dt.datetime.now(KST).strftime("%Y-%m-%d %H:%M")

    summary_html, shared_script = render_summary(
        draws, latest_draw, pred_filename, pred_data, all_predictions,
        dday_label, generated_at_label,
    )
    sidebar_html = render_sidebar(reports)
    next_draw_label = f'{pred_data["based_on_drwNo"] + 1}회차 예측 기준'

    html = f"""<title>로또 대시보드</title>
<script>
(function(){{
  try {{
    const saved = localStorage.getItem('lotto-theme');
    if (saved === 'dark' || saved === 'light') document.documentElement.dataset.theme = saved;
  }} catch (e) {{}}
}})();
</script>
<link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css">
<style>
  :root {{
    color-scheme: light;
    --blue-500: oklch(0.624 0.176 254);
    --blue-50:  oklch(0.965 0.020 250);
    --grey-900: oklch(0.234 0.030 254);
    --grey-700: oklch(0.452 0.028 253);
    --grey-400: oklch(0.752 0.016 251);
    --grey-200: oklch(0.913 0.008 247);
    --grey-100: oklch(0.957 0.005 247);
    --grey-50:  oklch(0.978 0.003 247);
    --white:    oklch(1.000 0.000 0);
    --red-500:  oklch(0.628 0.218 22);
    --green-500: oklch(0.493 0.143 154);
    --ball-yellow: oklch(0.853 0.156 86);
    --ball-blue:   oklch(0.624 0.176 254);
    --ball-red:    oklch(0.628 0.218 22);
    --ball-grey:   oklch(0.555 0.022 253);
    --ball-green:  oklch(0.493 0.143 154);
    --text-primary: var(--grey-900);
    --text-secondary: var(--grey-700);
    --text-tertiary: oklch(0.155 0.060 261 / 0.58);
    --border-secondary: var(--grey-200);
    --shadow-1: 0 1px 2px oklch(0.155 0.060 261 / 0.06), 0 1px 1px oklch(0.155 0.060 261 / 0.04);
  }}
  @media (prefers-color-scheme: dark) {{
    :root:not([data-theme="light"]) {{
      color-scheme: dark;
      --blue-500: #6f8fb8;
      --blue-50:  #24344a;
      --grey-900: #ecebe6;
      --grey-700: #b7b6ac;
      --grey-400: #85847a;
      --grey-200: #35363a;
      --grey-100: #232428;
      --grey-50:  #1d1e21;
      --white:    #16171a;
      --red-500:  #d9736b;
      --green-500: #4fa688;
      --text-tertiary: rgba(236, 235, 230, 0.58);
      --shadow-1: 0 1px 2px rgba(0, 0, 0, 0.30), 0 1px 1px rgba(0, 0, 0, 0.20);
    }}
  }}
  :root[data-theme="dark"] {{
    color-scheme: dark;
    --blue-500: #6f8fb8;
    --blue-50:  #24344a;
    --grey-900: #ecebe6;
    --grey-700: #b7b6ac;
    --grey-400: #85847a;
    --grey-200: #35363a;
    --grey-100: #232428;
    --grey-50:  #1d1e21;
    --white:    #16171a;
    --red-500:  #d9736b;
    --green-500: #4fa688;
    --text-tertiary: rgba(236, 235, 230, 0.58);
    --shadow-1: 0 1px 2px rgba(0, 0, 0, 0.30), 0 1px 1px rgba(0, 0, 0, 0.20);
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; color: var(--text-primary); background: var(--white);
    font-family: "Pretendard Variable", Pretendard, -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Noto Sans KR", Roboto, "Helvetica Neue", Arial, sans-serif;
  }}
  .h3 {{ font-size: 20px; font-weight: 700; line-height: 1.35; letter-spacing: -0.015em; margin: 0 0 12px; }}
  .body-1 {{ font-size: 15px; font-weight: 400; line-height: 1.5; letter-spacing: -0.005em; margin: 0; }}
  .caption {{ font-size: 12px; font-weight: 500; line-height: 1.4; color: var(--text-tertiary); margin: 8px 0 0; }}
  .footnote {{ font-size: 12px; font-weight: 500; line-height: 1.4; color: var(--text-tertiary); margin-top: 24px; }}
  .table-numeric {{ font-variant-numeric: tabular-nums; }}

  .top-nav {{
    height: 56px; flex: none; display: flex; align-items: center; gap: 12px; justify-content: space-between;
    padding: 0 20px; background: var(--white); border-bottom: 1px solid var(--border-secondary);
  }}
  .top-nav .title-1 {{ font-size: 18px; font-weight: 600; letter-spacing: -0.01em; }}
  .top-nav .caption {{ margin: 0; }}
  .menu-btn {{
    display: none; flex: none; width: 36px; height: 36px; border: none; background: none;
    border-radius: 12px; cursor: pointer; align-items: center; justify-content: center;
  }}
  .menu-btn:hover {{ background: var(--grey-100); }}
  .menu-btn svg {{ width: 20px; height: 20px; }}
  .theme-btn {{
    flex: none; width: 36px; height: 36px; border: none; background: none; color: var(--text-secondary);
    border-radius: 12px; cursor: pointer; align-items: center; justify-content: center; display: flex;
  }}
  .theme-btn:hover {{ background: var(--grey-100); }}
  .theme-btn svg {{ width: 18px; height: 18px; }}
  .theme-btn .icon-moon {{ display: none; }}
  :root[data-theme="dark"] .theme-btn .icon-sun {{ display: none; }}
  :root[data-theme="dark"] .theme-btn .icon-moon {{ display: block; }}
  @media (prefers-color-scheme: dark) {{
    :root:not([data-theme="light"]) .theme-btn .icon-sun {{ display: none; }}
    :root:not([data-theme="light"]) .theme-btn .icon-moon {{ display: block; }}
  }}
  .sidebar-backdrop {{ display: none; }}

  .layout {{ display: flex; height: calc(100vh - 56px); position: relative; }}
  .sidebar {{ width: 260px; flex: none; overflow-y: auto; border-right: 1px solid var(--border-secondary); background: var(--grey-50); }}

  @media (max-width: 768px) {{
    .menu-btn {{ display: inline-flex; }}
    .top-nav .caption {{ display: none; }}
    .layout {{ position: relative; overflow: hidden; }}
    .sidebar {{
      position: fixed; top: 56px; bottom: 0; left: 0; z-index: 20; width: 78vw; max-width: 320px;
      box-shadow: var(--shadow-1); transform: translateX(-100%); transition: transform 200ms cubic-bezier(0.16,1,0.3,1);
    }}
    .sidebar.is-open {{ transform: translateX(0); }}
    .sidebar-backdrop {{
      display: block; position: fixed; inset: 56px 0 0 0; background: oklch(0 0 0 / 0.32);
      z-index: 15; opacity: 0; pointer-events: none; transition: opacity 200ms ease;
    }}
    .sidebar-backdrop.is-open {{ opacity: 1; pointer-events: auto; }}
  }}
  .sidebar-title {{ font-size: 12px; font-weight: 700; color: var(--text-tertiary); letter-spacing: 0.02em; padding: 16px 16px 8px; margin: 0; }}
  .sidebar > ul {{ list-style: none; margin: 0; padding: 8px 8px 12px; }}
  .home-link {{
    display: block; padding: 8px 12px; margin: 8px 8px 6px; border-radius: 12px;
    font-size: 15px; font-weight: 600; color: var(--text-secondary); text-decoration: none;
    border-left: 3px solid transparent;
  }}
  .home-link:hover {{ background: var(--grey-100); }}
  .home-link.active {{ background: var(--blue-50); color: var(--blue-500); border-left-color: var(--blue-500); }}

  .draw-group {{ margin-bottom: 2px; }}
  .draw-group.is-hidden {{ display: none; }}
  .draw-header {{ width: 100%; display: flex; align-items: center; gap: 8px; background: none; border: none; cursor: pointer; padding: 8px 8px; border-radius: 12px; font: inherit; text-align: left; }}
  .draw-header:hover {{ background: var(--grey-100); }}
  .draw-header .chevron {{ font-size: 10px; color: var(--grey-400); transition: transform 200ms cubic-bezier(0.16,1,0.3,1); flex: none; }}
  .draw-header[aria-expanded="true"] .chevron {{ transform: rotate(90deg); }}
  .draw-label {{ flex: 1; font-size: 12.5px; font-weight: 600; }}
  .draw-count {{ font-size: 10.5px; color: var(--text-secondary); background: var(--grey-100); border-radius: 999px; padding: 1px 7px; font-variant-numeric: tabular-nums; }}
  .draw-body {{ list-style: none; margin: 0; padding: 0; max-height: 0; overflow: hidden; transition: max-height 200ms cubic-bezier(0.16,1,0.3,1); }}
  .draw-body[data-open="true"] {{ max-height: 400px; }}
  .draw-body li a {{ display: block; padding: 6px 10px 6px 27px; font-size: 12.5px; text-decoration: none; color: var(--text-secondary); border-radius: 12px; margin: 1px 4px; border-left: 3px solid transparent; font-variant-numeric: tabular-nums; }}
  .draw-body li a:hover {{ background: var(--grey-100); }}
  .draw-body li a.active {{ background: var(--blue-50); color: var(--blue-500); font-weight: 600; border-left-color: var(--blue-500); }}

  .main {{ flex: 1; overflow-y: auto; }}
  #dashboard-view {{
    max-width: 1440px; margin: 0 auto; padding: 20px; box-sizing: border-box;
    display: grid; grid-template-columns: repeat(auto-fit, minmax(min(340px, 100%), 1fr)); gap: 16px;
  }}
  #dashboard-view[hidden] {{ display: none; }}
  .dash-footer {{
    grid-column: 1 / -1; display: flex; gap: 16px; flex-wrap: wrap;
    padding-top: 16px; border-top: 1px solid var(--border-secondary);
  }}
  .dash-footer .footnote {{ margin: 0; }}
  .card {{
    border: 1px solid var(--border-secondary); border-radius: 16px; box-shadow: var(--shadow-1);
    padding: 20px; margin-bottom: 0;
  }}
  .card .h3 {{ margin-bottom: 12px; }}
  .pred-header {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; margin-bottom: 12px; }}
  .pred-header .h3 {{ margin: 0; }}
  .select-row {{ display: flex; gap: 8px; }}
  .select-row select {{
    font: inherit; font-size: 13px; font-weight: 600; color: var(--text-primary);
    background: var(--grey-50); border: 1px solid var(--border-secondary); border-radius: 8px;
    padding: 8px 12px; min-height: 32px; box-sizing: border-box; cursor: pointer;
  }}
  .number-ball {{
    display: inline-flex; align-items: center; justify-content: center;
    width: 32px; height: 32px; border-radius: 999px; margin-right: 6px;
    font-size: 15px; font-weight: 600; color: var(--white); font-variant-numeric: tabular-nums;
  }}
  .number-ball.ball-yellow {{ background: var(--ball-yellow); color: #1c1c1c; }}
  .number-ball.ball-blue {{ background: var(--ball-blue); }}
  .number-ball.ball-red {{ background: var(--ball-red); }}
  .number-ball.ball-grey {{ background: var(--ball-grey); }}
  .number-ball.ball-green {{ background: var(--ball-green); }}
  .number-ball.hit {{ outline: 2px solid var(--green-500); outline-offset: 1px; }}

  ul.pred-list {{ list-style: none; margin: 0; padding: 0; }}
  .pred-row {{ display: flex; align-items: center; gap: 12px; padding: 8px 0; border-bottom: 1px solid var(--border-secondary); }}
  .pred-row:last-child {{ border-bottom: none; }}
  .set-idx {{ color: var(--text-tertiary); width: 16px; font-size: 12px; font-weight: 500; flex: none; }}
  .set-nums {{ line-height: 1; }}
  .set-nums .number-ball {{ width: 28px; height: 28px; font-size: 13px; margin-right: 4px; }}

  .recent-list {{ list-style: none; margin: 0; padding: 0; }}
  .recent-row {{ display: flex; flex-direction: column; gap: 4px; padding: 8px 0; border-bottom: 1px solid var(--border-secondary); }}
  .recent-row:last-child {{ border-bottom: none; }}
  .recent-line {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; }}
  .recent-no {{ font-size: 13px; font-weight: 700; flex: none; }}
  .recent-date {{ font-size: 12px; color: var(--text-tertiary); flex: none; }}
  .recent-balls {{ line-height: 1; }}
  .recent-balls .number-ball {{ width: 26px; height: 26px; font-size: 12px; margin-right: 4px; }}
  .recent-amount {{ font-size: 12.5px; font-weight: 600; color: var(--text-secondary); flex: none; }}

  .accuracy-badge {{
    display: inline-flex; align-items: center; border-radius: 999px; padding: 2px 10px;
    font-size: 15px; font-weight: 600; background: var(--blue-50); color: var(--blue-500);
  }}
  .accuracy-badge.dim {{ background: var(--grey-100); color: var(--text-secondary); }}

  iframe {{ display: block; width: 100%; height: 100%; border: none; }}
  iframe[hidden] {{ display: none; }}
</style>
<header class="top-nav">
  <button class="menu-btn" id="menu-btn" type="button" aria-label="리포트 목록 열기" aria-expanded="false" aria-controls="sidebar">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="4" y1="7" x2="20" y2="7"/><line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="17" x2="20" y2="17"/></svg>
  </button>
  <span class="title-1">로또 대시보드</span>
  <span class="caption" style="flex:1">{next_draw_label}</span>
  <button class="theme-btn" id="theme-btn" type="button" aria-label="다크 모드 전환">
    <svg class="icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
    <svg class="icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
  </button>
</header>
<div class="layout">
  <div class="sidebar-backdrop" id="sidebar-backdrop"></div>
  <nav class="sidebar" id="sidebar">
    <h1 class="sidebar-title">리포트 목록</h1>
    <a href="#" id="home-link" class="home-link active">대시보드 홈</a>
    <ul id="group-list">
{sidebar_html}
    </ul>
  </nav>
  <main class="main">
    <div id="dashboard-view">{summary_html}
    </div>
    <iframe id="viewer" title="선택한 회차 리포트" hidden></iframe>
  </main>
</div>
<script>
{shared_script}

const dashboardView = document.getElementById('dashboard-view');
const viewer = document.getElementById('viewer');

const homeLink = document.getElementById('home-link');
const navLinks = [homeLink, ...document.querySelectorAll('.draw-body a')];

const sidebar = document.getElementById('sidebar');
const sidebarBackdrop = document.getElementById('sidebar-backdrop');
const menuBtn = document.getElementById('menu-btn');
const themeBtn = document.getElementById('theme-btn');

function currentTheme() {{
  return document.documentElement.dataset.theme
    || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
}}
function syncIframeTheme() {{
  try {{
    const doc = viewer.contentDocument;
    if (doc && doc.documentElement) doc.documentElement.dataset.theme = currentTheme();
  }} catch (e) {{}}
}}
themeBtn.addEventListener('click', () => {{
  const next = currentTheme() === 'dark' ? 'light' : 'dark';
  document.documentElement.dataset.theme = next;
  try {{ localStorage.setItem('lotto-theme', next); }} catch (e) {{}}
  syncIframeTheme();
}});
viewer.addEventListener('load', syncIframeTheme);

function closeSidebar() {{
  sidebar.classList.remove('is-open');
  sidebarBackdrop.classList.remove('is-open');
  menuBtn.setAttribute('aria-expanded', 'false');
}}
function openSidebar() {{
  sidebar.classList.add('is-open');
  sidebarBackdrop.classList.add('is-open');
  menuBtn.setAttribute('aria-expanded', 'true');
}}
menuBtn.addEventListener('click', () => {{
  sidebar.classList.contains('is-open') ? closeSidebar() : openSidebar();
}});
sidebarBackdrop.addEventListener('click', closeSidebar);

document.querySelectorAll('.draw-body a').forEach(a => {{
  a.addEventListener('click', (e) => {{
    e.preventDefault();
    viewer.src = a.dataset.src;
    viewer.hidden = false;
    dashboardView.hidden = true;
    navLinks.forEach(el => el.classList.remove('active'));
    a.classList.add('active');
    closeSidebar();
  }});
}});

document.querySelectorAll('button.draw-header').forEach(btn => {{
  btn.addEventListener('click', () => {{
    const open = btn.getAttribute('aria-expanded') === 'true';
    btn.setAttribute('aria-expanded', open ? 'false' : 'true');
    const body = btn.nextElementSibling;
    body.setAttribute('data-open', open ? 'false' : 'true');
    // 그룹을 펼칠 때는 그 안의 최신 리포트(맨 위 항목)를 바로 선택해서 보여준다.
    if (!open) {{
      const firstLink = body.querySelector('a');
      if (firstLink) firstLink.click();
    }}
  }});
}});

homeLink.addEventListener('click', (e) => {{
  e.preventDefault();
  viewer.hidden = true;
  dashboardView.hidden = false;
  navLinks.forEach(el => el.classList.remove('active'));
  homeLink.classList.add('active');
  closeSidebar();
}});
</script>
"""
    OUTPUT_PATH.write_text(html, encoding="utf-8")
    print(f"대시보드 생성됨 -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
