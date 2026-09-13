"""reports/ 안의 lotto_report_<timestamp>.html 파일들을 스캔해서
reports/index.html을 생성한다. 최신 리포트를 iframe으로 바로 보여주고,
좌측 목록에서 과거 리포트를 선택하면 iframe이 해당 리포트로 바뀐다.
"""
import datetime as dt
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = ROOT / "reports"
FILENAME_RE = re.compile(r"^lotto_report_(\d{8})_(\d{6})\.html$")


def list_reports():
    reports = []
    for path in REPORT_DIR.glob("lotto_report_*.html"):
        m = FILENAME_RE.match(path.name)
        if not m:
            continue
        timestamp = dt.datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S")
        reports.append((timestamp, path.name))
    reports.sort(key=lambda r: r[0], reverse=True)
    return reports


def render_index(reports):
    latest_name = reports[0][1]
    items = "\n".join(
        f'      <li><a href="#" data-src="{name}" class="{"active" if name == latest_name else ""}">'
        f'{ts.strftime("%Y-%m-%d %H:%M")}</a></li>'
        for ts, name in reports
    )
    return f"""<title>로또 분석 리포트</title>
<style>
  body {{ margin: 0; font-family: system-ui, sans-serif; }}
  .layout {{ display: flex; height: 100vh; }}
  .sidebar {{ width: 220px; flex: none; overflow-y: auto; border-right: 1px solid #ddd; padding: 12px 0; }}
  .sidebar h1 {{ font-size: 14px; padding: 0 16px; margin: 0 0 8px; }}
  .sidebar ul {{ list-style: none; margin: 0; padding: 0; }}
  .sidebar li a {{ display: block; padding: 8px 16px; font-size: 13px; text-decoration: none; color: #333; }}
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
