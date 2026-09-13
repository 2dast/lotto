"""reports/ 안의 lotto_report_<timestamp>.html 파일들을 스캔해서
reports/index.html을 생성한다. 최신 리포트를 iframe으로 바로 보여주고,
좌측 목록은 기준 회차별로 묶어서 보여주며, 항목마다 생성 일자/일시를 표시한다.
같은 회차를 여러 번 생성해도(수동 재실행 등) 회차 그룹 안에 모이도록 한다.
"""
import datetime as dt
import itertools
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = ROOT / "reports"
FILENAME_RE = re.compile(r"^lotto_report_(\d{8})_(\d{6})\.html$")
BASEDON_RE = re.compile(r'id="f-basedon">(\d+)<')


def list_reports():
    reports = []
    for path in REPORT_DIR.glob("lotto_report_*.html"):
        m = FILENAME_RE.match(path.name)
        if not m:
            continue
        timestamp = dt.datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S")
        basedon_m = BASEDON_RE.search(path.read_text(encoding="utf-8"))
        based_on = int(basedon_m.group(1)) if basedon_m else 0
        next_draw = based_on + 1  # 예측 대상은 마지막 발표 회차의 "다음" 회차
        reports.append((next_draw, timestamp, path.name))
    reports.sort(key=lambda r: (r[0], r[1]), reverse=True)
    return reports


def render_index(reports):
    latest_name = reports[0][2]

    sections = []
    for next_draw, group in itertools.groupby(reports, key=lambda r: r[0]):
        group = list(group)
        items = "\n".join(
            f'        <li><a href="#" data-src="{name}" class="{"active" if name == latest_name else ""}">'
            f'{ts.strftime("%Y-%m-%d %H:%M")}</a></li>'
            for _, ts, name in group
        )
        sections.append(f"""      <li class="draw-group">
        <div class="draw-label">{next_draw}회차 예측 ({len(group)}건)</div>
        <ul>
{items}
        </ul>
      </li>""")
    items = "\n".join(sections)

    return f"""<title>로또 분석 리포트</title>
<style>
  body {{ margin: 0; font-family: system-ui, sans-serif; }}
  .layout {{ display: flex; height: 100vh; }}
  .sidebar {{ width: 240px; flex: none; overflow-y: auto; border-right: 1px solid #ddd; padding: 12px 0; }}
  .sidebar h1 {{ font-size: 14px; padding: 0 16px; margin: 0 0 8px; }}
  .sidebar > ul {{ list-style: none; margin: 0; padding: 0; }}
  .draw-label {{ padding: 8px 16px 4px; font-size: 11px; font-weight: 700; color: #888; letter-spacing: 0.02em; }}
  .draw-group ul {{ list-style: none; margin: 0; padding: 0; }}
  .sidebar li a {{ display: block; padding: 6px 16px 6px 24px; font-size: 13px; text-decoration: none; color: #333; font-variant-numeric: tabular-nums; }}
  .sidebar li a:hover {{ background: #f0f0f0; }}
  .sidebar li a.active {{ background: #e4e9ef; font-weight: 700; color: #1f3a5f; }}
  iframe {{ flex: 1; border: none; }}
</style>
<div class="layout">
  <nav class="sidebar">
    <h1>과거 리포트</h1>
    <ul>
{items}
    </ul>
  </nav>
  <iframe id="viewer" src="{latest_name}"></iframe>
</div>
<script>
document.querySelectorAll('.sidebar a').forEach(a => {{
  a.addEventListener('click', (e) => {{
    e.preventDefault();
    document.getElementById('viewer').src = a.dataset.src;
    document.querySelectorAll('.sidebar a').forEach(el => el.classList.remove('active'));
    a.classList.add('active');
  }});
}});
</script>
"""


def main():
    reports = list_reports()
    if not reports:
        print("reports/ 에 생성된 리포트가 없습니다.")
        return
    (REPORT_DIR / "index.html").write_text(render_index(reports), encoding="utf-8")
    print(f"reports/index.html 생성 완료 ({len(reports)}개 리포트)")


if __name__ == "__main__":
    main()
