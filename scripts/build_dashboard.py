"""저장소 루트에 index.html 대시보드를 생성한다. 메인 화면은 최신 실제 당첨번호,
다음 회차 예측 5세트, 적중 이력 추세를 보여주고, 왼쪽 사이드바에서 회차별 리포트를
선택하면 같은 화면 안에서 그 리포트(reports/lotto_report_<ts>.html)를 바로 보여준다.
(reports/ 안의 회차 그룹핑은 build_index.list_reports를 그대로 재사용한다.)

화면 톤은 design.md(토스 디자인 시스템 토큰 기반)를 따른다.
"""
import itertools
import json
from pathlib import Path

from build_index import list_reports

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "draws.json"
PREDICTIONS_DIR = ROOT / "predictions"
OUTPUT_PATH = ROOT / "index.html"

BALL_COLORS = ["ball-yellow", "ball-blue", "ball-red", "ball-grey", "ball-green"]


def ball_zone(n: int) -> str:
    return BALL_COLORS[min((n - 1) // 10, 4)]


def number_ball(n: int, hit: bool = False) -> str:
    cls = f"number-ball {ball_zone(n)}" + (" hit" if hit else "")
    return f'<span class="{cls}">{n}</span>'


def load_latest_predictions() -> tuple[str, dict]:
    files = sorted(PREDICTIONS_DIR.glob("predictions_*.json"))
    latest = files[-1]
    return latest.name, json.loads(latest.read_text(encoding="utf-8"))


def load_all_predictions() -> list[dict]:
    """predictions/ 안의 모든 예측 파일을 회차 선택 드롭다운용으로 모은다."""
    entries = []
    for path in sorted(PREDICTIONS_DIR.glob("predictions_*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        entries.append({
            "file": path.name,
            "based_on_drwNo": data["based_on_drwNo"],
            "next_draw": data["based_on_drwNo"] + 1,
            "generated_at": data["generated_at"],
            "predictions": data["predictions"],
        })
    entries.sort(key=lambda e: e["generated_at"], reverse=True)
    return entries


def render_summary(
    draws: list[dict],
    latest_draw: dict,
    pred_filename: str,
    pred_data: dict,
    all_predictions: list[dict],
) -> tuple[str, str]:
    """대시보드 메인 화면(요약 + 예측 + 추세)의 HTML과 <script>를 반환한다.

    적중 이력은 별도 파일에 미리 계산해두지 않고, 선택된 예측 파일과 실제 당첨번호를
    그 자리에서 비교해 클라이언트에서 계산한다 — 같은 회차에 예측 파일이 여러 개
    있어도(재실행 등) 고른 파일 기준으로 항상 정확한 적중 결과를 보여준다.
    """
    based_on = pred_data["based_on_drwNo"]
    next_draw = based_on + 1
    latest_balls = " ".join(number_ball(n) for n in latest_draw["numbers"])

    rounds = sorted({e["next_draw"] for e in all_predictions}, reverse=True)
    round_options = "\n".join(
        f'          <option value="{r}"{" selected" if r == next_draw else ""}>{r}회차</option>'
        for r in rounds
    )

    predictions_json = json.dumps(all_predictions, ensure_ascii=False)
    draws_by_no_json = json.dumps({d["drwNo"]: d["numbers"] for d in draws}, ensure_ascii=False)

    pred_select_script = f"""
    const PREDICTIONS = {predictions_json};
    const DRAWS_BY_NO = {draws_by_no_json};
    const LATEST_DRWNO = {latest_draw["drwNo"]};
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
    const predFileCaption = document.getElementById('pred-file-caption');
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

    function renderPrediction(round, filename) {{
      const entry = PREDICTIONS.find(p => p.next_draw === Number(round) && p.file === filename);
      if (!entry) return;
      predTitle.textContent = `${{entry.next_draw}}회차 예측`;
      predFileCaption.textContent = `예측 파일: ${{entry.file}}`;

      const actualNumbers = DRAWS_BY_NO[entry.next_draw];
      if (actualNumbers) {{
        const hits = computeHits(entry.predictions, actualNumbers);
        const best = Math.max(...hits);
        const badges = hits.map(h => `<span class="accuracy-badge${{h === 0 ? ' dim' : ''}}">${{h}}개</span>`).join(' ');
        predSummary.innerHTML = `${{entry.next_draw}}회차 결과 대비 5세트 적중 ${{badges}} (최고 ${{best}}개)`;
        const hitSet = new Set(actualNumbers);
        predList.innerHTML = entry.predictions.map((combo, i) => `
          <li class="pred-row">
            <span class="set-idx">${{i + 1}}</span>
            <span class="set-nums">${{combo.map(n => ballHtml(n, hitSet.has(n))).join(' ')}}</span>
          </li>
        `).join('');
      }} else {{
        predSummary.textContent = '아직 추첨 전입니다 — 결과 발표 후 적중 이력이 집계됩니다.';
        predList.innerHTML = entry.predictions.map((combo, i) => `
          <li class="pred-row">
            <span class="set-idx">${{i + 1}}</span>
            <span class="set-nums">${{combo.map(n => ballHtml(n, false)).join(' ')}}</span>
          </li>
        `).join('');
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

    trend_script = f"""
    (function(){{
      const svg = document.getElementById("chart-trend");
      const caption = document.getElementById("trend-caption");
      if (!svg) return;

      // 회차별로 실제 결과가 이미 나온 예측만, 같은 회차에 여러 파일이 있으면
      // 가장 나중에 생성된 파일을 그 회차의 대표 기록으로 삼는다.
      const byRound = {{}};
      PREDICTIONS.forEach(p => {{
        if (!DRAWS_BY_NO[p.next_draw]) return;
        const cur = byRound[p.next_draw];
        if (!cur || p.generated_at > cur.generated_at) byRound[p.next_draw] = p;
      }});
      const HISTORY = Object.values(byRound).map(p => {{
        const hits = computeHits(p.predictions, DRAWS_BY_NO[p.next_draw]);
        return {{drwNo: p.next_draw, best: Math.max(...hits), avg: hits.reduce((a, b) => a + b, 0) / hits.length}};
      }}).sort((a, b) => a.drwNo - b.drwNo);

      if (HISTORY.length === 0) {{
        svg.hidden = true;
        caption.textContent = "아직 적중 이력 없음 — 다음 회차 추첨 이후부터 집계가 시작됩니다.";
        return;
      }}
      caption.textContent = "회차별 5세트 중 최고 적중개수(막대) — 무작위 기대값 0.8개와 비교, 최고 기록만 강조.";

      const styles = getComputedStyle(document.documentElement);
      const brand = styles.getPropertyValue("--blue-500").trim();
      const grey = styles.getPropertyValue("--grey-200").trim();
      const danger = styles.getPropertyValue("--red-500").trim();
      const W = 600, H = 200, padL = 30, padR = 10, padT = 10, padB = 24;
      const plotW = W - padL - padR, plotH = H - padT - padB;
      const n = HISTORY.length;
      const gap = 6;
      const barW = (plotW - gap * (n - 1)) / n;
      const maxV = Math.max(...HISTORY.map(h => h.best), 1);
      const peakBest = Math.max(...HISTORY.map(h => h.best));
      function el(tag, attrs) {{
        const e = document.createElementNS("http://www.w3.org/2000/svg", tag);
        for (const k in attrs) e.setAttribute(k, attrs[k]);
        return e;
      }}
      const baselineY = H - padB - (0.8 / maxV) * plotH;
      svg.appendChild(el("line", {{x1: padL, y1: baselineY, x2: W - padR, y2: baselineY, stroke: danger, "stroke-dasharray": "4 3"}}));
      HISTORY.forEach((h, i) => {{
        const x = padL + i * (barW + gap);
        const barH = (h.best / maxV) * plotH;
        const y = H - padB - barH;
        svg.appendChild(el("rect", {{x, y, width: barW, height: Math.max(barH, 1), rx: 2, fill: h.best === peakBest ? brand : grey}}));
        const lbl = el("text", {{x: x + barW / 2, y: H - padB + 14, "text-anchor": "middle", "font-size": "9", fill: styles.getPropertyValue("--text-tertiary").trim()}});
        lbl.textContent = h.drwNo;
        svg.appendChild(lbl);
      }});
    }})();"""

    trend_section = """
      <section class="card">
        <h2 class="h3">적중 이력 추세</h2>
        <svg id="chart-trend" viewBox="0 0 600 200" width="100%"></svg>
        <p class="caption" id="trend-caption"></p>
      </section>"""

    html = f"""
      <p class="body-1">최근 실제 당첨 · <span class="table-numeric">{latest_draw["drwNo"]}회차</span> ({latest_draw["date"]})</p>
      <p class="ball-row">{latest_balls}</p>

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
        <p class="body-1" id="pred-summary" style="margin:0 0 12px"></p>
        <ul class="pred-list" id="pred-list"></ul>
        <p class="caption" id="pred-file-caption">예측 파일: {pred_filename}</p>
      </section>
{trend_section}
      <p class="footnote">본 예측은 통계적 근거가 없으며 오락 목적입니다. 로또는 완전 무작위 추첨입니다.</p>"""
    return html, pred_select_script + trend_script


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
          <button class="draw-header" type="button" aria-expanded="{'true' if gi == 0 else 'false'}">
            <span class="chevron">&#9656;</span>
            <span class="draw-label">{next_draw}회차 예측</span>
            <span class="draw-count">{len(group)}</span>
          </button>
          <ul class="draw-body"{' data-open="true"' if gi == 0 else ''}>
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

    summary_html, trend_script = render_summary(
        draws, latest_draw, pred_filename, pred_data, all_predictions
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
  .draw-count {{ font-size: 10.5px; color: var(--text-secondary); background: var(--grey-100); border-radius: 999px; padding: 1px 7px; }}
  .draw-body {{ list-style: none; margin: 0; padding: 0; max-height: 0; overflow: hidden; transition: max-height 200ms cubic-bezier(0.16,1,0.3,1); }}
  .draw-body[data-open="true"] {{ max-height: 400px; }}
  .draw-body li a {{ display: block; padding: 6px 10px 6px 27px; font-size: 12.5px; text-decoration: none; color: var(--text-secondary); border-radius: 12px; margin: 1px 4px; border-left: 3px solid transparent; }}
  .draw-body li a:hover {{ background: var(--grey-100); }}
  .draw-body li a.active {{ background: var(--blue-50); color: var(--blue-500); font-weight: 600; border-left-color: var(--blue-500); }}

  .main {{ flex: 1; overflow-y: auto; }}
  #dashboard-view {{ max-width: 640px; margin: 0 auto; padding: 24px 20px 64px; }}
  .card {{
    border: 1px solid var(--border-secondary); border-radius: 16px; box-shadow: var(--shadow-1);
    padding: 20px; margin-bottom: 16px;
  }}
  .pred-header {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; margin-bottom: 12px; }}
  .pred-header .h3 {{ margin: 0; }}
  .select-row {{ display: flex; gap: 8px; }}
  .select-row select {{
    font: inherit; font-size: 13px; font-weight: 600; color: var(--text-primary);
    background: var(--grey-50); border: 1px solid var(--border-secondary); border-radius: 8px;
    padding: 6px 10px; cursor: pointer;
  }}
  .ball-row {{ margin: 8px 0 24px; line-height: 1; display: flex; flex-wrap: wrap; gap: 6px; }}
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

  .accuracy-badge {{
    display: inline-flex; align-items: center; border-radius: 999px; padding: 2px 10px;
    font-size: 15px; font-weight: 600; background: var(--blue-50); color: var(--blue-500);
  }}
  .accuracy-badge.dim {{ background: var(--grey-100); color: var(--text-secondary); }}

  iframe {{ display: block; width: 100%; height: 100%; border: none; }}
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
{trend_script}

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

document.querySelectorAll('.draw-header').forEach(btn => {{
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
