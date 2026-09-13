"""저장소 루트에 index.html 대시보드를 생성한다. 메인 화면은 최신 실제 당첨번호,
다음 회차 예측 5세트, 적중 이력 추세를 보여주고, 왼쪽 사이드바에서 회차별 리포트를
선택하면 같은 화면 안에서 그 리포트(reports/lotto_report_<ts>.html)를 바로 보여준다.
(reports/ 안의 회차 그룹핑은 build_index.list_reports를 그대로 재사용한다.)
"""
import json
from pathlib import Path

from build_index import list_reports

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "draws.json"
PREDICTIONS_DIR = ROOT / "predictions"
HISTORY_PATH = ROOT / "data" / "accuracy_history.json"
OUTPUT_PATH = ROOT / "index.html"


def load_latest_predictions() -> tuple[str, dict]:
    files = sorted(PREDICTIONS_DIR.glob("predictions_*.json"))
    latest = files[-1]
    return latest.name, json.loads(latest.read_text(encoding="utf-8"))


def load_history() -> list[dict]:
    if not HISTORY_PATH.exists():
        return []
    return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))


def render_summary(latest_draw: dict, pred_filename: str, pred_data: dict, history: list[dict]) -> tuple[str, str]:
    """대시보드 메인 화면(요약 + 예측 + 추세)의 HTML과 <script>를 반환한다."""
    based_on = pred_data["based_on_drwNo"]
    next_draw = based_on + 1
    pred_rows = "\n".join(
        f'          <li><span class="set-idx">{i + 1}</span>'
        f'<span class="set-nums">{" · ".join(str(n) for n in combo)}</span></li>'
        for i, combo in enumerate(pred_data["predictions"])
    )

    if history:
        last = history[-1]
        last_hits_summary = (
            f'{last["drwNo"]}회차 실제 결과 대비 5세트 적중: '
            f'{", ".join(str(h) for h in last["hits"])}개 (최고 {max(last["hits"])}개)'
        )
        history_json = json.dumps(
            [{"drwNo": e["drwNo"], "best": max(e["hits"]), "avg": round(sum(e["hits"]) / len(e["hits"]), 2)}
             for e in history],
            ensure_ascii=False,
        )
        trend_section = """
      <section>
        <h2>적중 이력 추세</h2>
        <svg id="chart-trend" viewBox="0 0 600 200" width="100%"></svg>
        <p class="note">회차별 5세트 중 최고 적중개수(막대) — 무작위 기대값 0.8개와 비교.</p>
      </section>"""
        trend_script = f"""
    const HISTORY = {history_json};
    (function(){{
      const svg = document.getElementById("chart-trend");
      if (!svg) return;
      const W = 600, H = 200, padL = 30, padR = 10, padT = 10, padB = 24;
      const plotW = W - padL - padR, plotH = H - padT - padB;
      const n = HISTORY.length;
      const gap = 6;
      const barW = (plotW - gap * (n - 1)) / n;
      const maxV = Math.max(...HISTORY.map(h => h.best), 1);
      function el(tag, attrs) {{
        const e = document.createElementNS("http://www.w3.org/2000/svg", tag);
        for (const k in attrs) e.setAttribute(k, attrs[k]);
        return e;
      }}
      svg.appendChild(el("line", {{x1: padL, y1: H - padB, x2: W - padR, y2: H - padB, stroke: "#999"}}));
      const baselineY = H - padB - (0.8 / maxV) * plotH;
      svg.appendChild(el("line", {{x1: padL, y1: baselineY, x2: W - padR, y2: baselineY, stroke: "#a5322b", "stroke-dasharray": "4 3"}}));
      HISTORY.forEach((h, i) => {{
        const x = padL + i * (barW + gap);
        const barH = (h.best / maxV) * plotH;
        const y = H - padB - barH;
        svg.appendChild(el("rect", {{x, y, width: barW, height: Math.max(barH, 1), fill: "#1f3a5f"}}));
        const lbl = el("text", {{x: x + barW / 2, y: H - padB + 14, "text-anchor": "middle", "font-size": "9"}});
        lbl.textContent = h.drwNo;
        svg.appendChild(lbl);
      }});
    }})();"""
    else:
        last_hits_summary = "아직 적중 이력 없음 — 다음 회차부터 집계 시작"
        trend_section = """
      <section>
        <h2>적중 이력 추세</h2>
        <p class="note">아직 적중 이력 없음 — 다음 회차 추첨 이후부터 집계가 시작됩니다.</p>
      </section>"""
        trend_script = ""

    html = f"""
      <p class="note">최근 실제 당첨: {latest_draw["drwNo"]}회차 ({latest_draw["date"]}) — {", ".join(str(n) for n in latest_draw["numbers"])}</p>
      <section>
        <h2>{next_draw}회차 예측</h2>
        <div class="summary-box">{last_hits_summary}</div>
        <ul class="pred-list">
{pred_rows}
        </ul>
        <p class="note">예측 파일: {pred_filename}</p>
      </section>
{trend_section}"""
    return html, trend_script


def render_sidebar(reports: list[tuple[int, object, str]]) -> str:
    """reports/index.html과 동일한 회차별 아코디언 목록을 사이드바에 그대로 재사용한다."""
    if not reports:
        return '<p class="note" style="padding:8px 16px">아직 생성된 리포트가 없습니다.</p>'

    import itertools

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
    history = load_history()
    reports = list_reports()

    summary_html, trend_script = render_summary(latest_draw, pred_filename, pred_data, history)
    sidebar_html = render_sidebar(reports)

    html = f"""<title>로또 대시보드</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; font-family: "Noto Sans KR", system-ui, sans-serif; color: #1c1c1c; }}
  .layout {{ display: flex; height: 100vh; }}
  .sidebar {{ width: 260px; flex: none; overflow-y: auto; border-right: 1px solid #e4e2da; background: #fbfaf7; }}
  .sidebar h1 {{ font-size: 13px; font-weight: 700; padding: 16px 16px 10px; margin: 0; }}
  .sidebar > ul {{ list-style: none; margin: 0; padding: 0 8px 12px; }}
  .home-link {{ display: block; padding: 8px 8px; margin: 0 8px 6px; border-radius: 6px; font-size: 12.5px; font-weight: 700; color: #1f3a5f; text-decoration: none; background: #e4e9ef; }}

  .draw-group {{ margin-bottom: 2px; }}
  .draw-group.is-hidden {{ display: none; }}
  .draw-header {{ width: 100%; display: flex; align-items: center; gap: 8px; background: none; border: none; cursor: pointer; padding: 8px 8px; border-radius: 6px; font: inherit; text-align: left; }}
  .draw-header:hover {{ background: #f0efe8; }}
  .draw-header .chevron {{ font-size: 10px; color: #9a9a90; transition: transform 0.15s ease; flex: none; }}
  .draw-header[aria-expanded="true"] .chevron {{ transform: rotate(90deg); }}
  .draw-label {{ flex: 1; font-size: 12.5px; font-weight: 600; }}
  .draw-count {{ font-size: 10.5px; color: #8a8878; background: #ecebe3; border-radius: 10px; padding: 1px 7px; }}
  .draw-body {{ list-style: none; margin: 0; padding: 0; max-height: 0; overflow: hidden; transition: max-height 0.2s ease; }}
  .draw-body[data-open="true"] {{ max-height: 400px; }}
  .draw-body li a {{ display: block; padding: 6px 10px 6px 30px; font-size: 12.5px; text-decoration: none; color: #55534a; border-radius: 6px; margin: 1px 4px; }}
  .draw-body li a:hover {{ background: #f0efe8; }}
  .draw-body li a.active {{ background: #1f3a5f; color: #fff; font-weight: 600; }}

  .main {{ flex: 1; overflow-y: auto; }}
  #dashboard-view {{ max-width: 640px; margin: 0 auto; padding: 24px 20px 60px; }}
  #dashboard-view h2 {{ font-size: 14px; border-bottom: 1.5px solid #1c1c1c; padding-bottom: 6px; }}
  #dashboard-view section {{ margin-bottom: 28px; }}
  .summary-box {{ background: #ecebe3; border-left: 3px solid #1f3a5f; padding: 12px 16px; font-size: 13px; margin-bottom: 8px; }}
  ul.pred-list {{ list-style: none; margin: 0; padding: 0; }}
  ul.pred-list li {{ display: flex; gap: 12px; padding: 6px 0; border-bottom: 1px solid #eee; font-variant-numeric: tabular-nums; }}
  .set-idx {{ color: #8a8878; width: 16px; }}
  .note {{ font-size: 12px; color: #6b6a60; }}
  iframe {{ width: 100%; height: 100%; border: none; }}
</style>
<div class="layout">
  <nav class="sidebar">
    <h1>로또 대시보드</h1>
    <a href="#" id="home-link" class="home-link">대시보드 홈</a>
    <ul id="group-list">
{sidebar_html}
    </ul>
  </nav>
  <main class="main">
    <div id="dashboard-view">{summary_html}
    </div>
    <iframe id="viewer" hidden></iframe>
  </main>
</div>
<script>
{trend_script}

document.querySelectorAll('.draw-header').forEach(btn => {{
  btn.addEventListener('click', () => {{
    const open = btn.getAttribute('aria-expanded') === 'true';
    btn.setAttribute('aria-expanded', open ? 'false' : 'true');
    btn.nextElementSibling.setAttribute('data-open', open ? 'false' : 'true');
  }});
}});

const dashboardView = document.getElementById('dashboard-view');
const viewer = document.getElementById('viewer');

document.querySelectorAll('.draw-body a').forEach(a => {{
  a.addEventListener('click', (e) => {{
    e.preventDefault();
    viewer.src = a.dataset.src;
    viewer.hidden = false;
    dashboardView.hidden = true;
    document.querySelectorAll('.draw-body a').forEach(el => el.classList.remove('active'));
    a.classList.add('active');
  }});
}});

document.getElementById('home-link').addEventListener('click', (e) => {{
  e.preventDefault();
  viewer.hidden = true;
  dashboardView.hidden = false;
  document.querySelectorAll('.draw-body a').forEach(el => el.classList.remove('active'));
}});
</script>
"""
    OUTPUT_PATH.write_text(html, encoding="utf-8")
    print(f"대시보드 생성됨 -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
