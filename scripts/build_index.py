"""reports/ 안의 lotto_report_<timestamp>.html 파일들을 스캔해서
reports/index.html을 생성한다. 최신 리포트를 iframe으로 바로 보여주고,
좌측 목록은 예측 대상 회차별 아코디언으로 묶고, 최근 10개 회차만 먼저 보여준 뒤
"더보기"로 이전 회차를 펼친다.
"""
import datetime as dt
import itertools
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = ROOT / "reports"
FILENAME_RE = re.compile(r"^lotto_report_(\d{8})_(\d{6})\.html$")
BASEDON_RE = re.compile(r'id="f-basedon">(\d+)<')
VISIBLE_GROUPS = 10


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

    groups = []
    for next_draw, group in itertools.groupby(reports, key=lambda r: r[0]):
        groups.append((next_draw, list(group)))

    sections = []
    for gi, (next_draw, group) in enumerate(groups):
        is_first = gi == 0
        hidden_group = gi >= VISIBLE_GROUPS
        items = "\n".join(
            f'          <li><a href="#" data-src="{name}" class="{"active" if name == latest_name else ""}">'
            f'{ts.strftime("%Y-%m-%d %H:%M")}</a></li>'
            for _, ts, name in group
        )
        sections.append(f"""      <li class="draw-group{' is-hidden' if hidden_group else ''}" data-group-index="{gi}">
        <button class="draw-header" type="button" aria-expanded="{'true' if is_first else 'false'}">
          <span class="chevron">&#9656;</span>
          <span class="draw-label">{next_draw}회차 예측</span>
          <span class="draw-count">{len(group)}</span>
        </button>
        <ul class="draw-body"{' data-open="true"' if is_first else ''}>
{items}
        </ul>
      </li>""")
    items = "\n".join(sections)

    remaining = max(len(groups) - VISIBLE_GROUPS, 0)
    more_button = (
        f'    <button id="more-btn" type="button" data-remaining="{remaining}">'
        f'더보기 ({remaining}개 회차)</button>\n' if remaining > 0 else ""
    )

    return f"""<title>로또 분석 리포트</title>
<link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css">
<style>
  :root {{
    --blue-500: oklch(0.624 0.176 254);
    --blue-50:  oklch(0.965 0.020 250);
    --grey-900: oklch(0.234 0.030 254);
    --grey-700: oklch(0.452 0.028 253);
    --grey-400: oklch(0.752 0.016 251);
    --grey-200: oklch(0.913 0.008 247);
    --grey-100: oklch(0.957 0.005 247);
    --grey-50:  oklch(0.978 0.003 247);
    --white:    oklch(1.000 0.000 0);
    --text-primary: var(--grey-900);
    --text-secondary: var(--grey-700);
    --border-secondary: var(--grey-200);
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; color: var(--text-primary);
    font-family: "Pretendard Variable", Pretendard, -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Noto Sans KR", Roboto, "Helvetica Neue", Arial, sans-serif;
  }}
  .top-nav {{
    display: none; height: 56px; flex: none; align-items: center; gap: 12px;
    padding: 0 16px; background: var(--white); border-bottom: 1px solid var(--border-secondary);
  }}
  .top-nav .title-1 {{ font-size: 16px; font-weight: 600; letter-spacing: -0.01em; }}
  .menu-btn {{
    flex: none; width: 36px; height: 36px; border: none; background: none;
    border-radius: 12px; cursor: pointer; align-items: center; justify-content: center; display: flex;
  }}
  .menu-btn:hover {{ background: var(--grey-100); }}
  .menu-btn svg {{ width: 20px; height: 20px; }}
  .sidebar-backdrop {{ display: none; }}

  .layout {{ display: flex; height: 100vh; flex-direction: column; }}
  .layout-body {{ display: flex; flex: 1; min-height: 0; }}
  .sidebar {{ width: 260px; flex: none; overflow-y: auto; border-right: 1px solid var(--border-secondary); background: var(--grey-50); }}
  .sidebar h1 {{ height: 56px; display: flex; align-items: center; font-size: 18px; font-weight: 600; letter-spacing: -0.01em; padding: 0 16px; margin: 0; border-bottom: 1px solid var(--border-secondary); }}
  .sidebar > ul {{ list-style: none; margin: 0; padding: 8px 8px 12px; }}

  @media (max-width: 768px) {{
    .top-nav {{ display: flex; }}
    .layout-body {{ position: relative; overflow: hidden; }}
    .sidebar {{
      position: fixed; top: 56px; bottom: 0; left: 0; z-index: 20; width: 78vw; max-width: 320px;
      box-shadow: var(--shadow-1); transform: translateX(-100%); transition: transform 200ms cubic-bezier(0.16,1,0.3,1);
    }}
    .sidebar h1 {{ display: none; }}
    .sidebar.is-open {{ transform: translateX(0); }}
    .sidebar-backdrop {{
      display: block; position: fixed; inset: 56px 0 0 0; background: oklch(0 0 0 / 0.32);
      z-index: 15; opacity: 0; pointer-events: none; transition: opacity 200ms ease;
    }}
    .sidebar-backdrop.is-open {{ opacity: 1; pointer-events: auto; }}
  }}

  .draw-group {{ margin-bottom: 2px; }}
  .draw-group.is-hidden {{ display: none; }}

  .draw-header {{
    width: 100%; display: flex; align-items: center; gap: 8px;
    background: none; border: none; cursor: pointer;
    padding: 8px 8px; border-radius: 12px; font: inherit; text-align: left;
  }}
  .draw-header:hover {{ background: var(--grey-100); }}
  .draw-header .chevron {{
    font-size: 10px; color: var(--grey-400); transition: transform 200ms cubic-bezier(0.16,1,0.3,1); flex: none;
  }}
  .draw-header[aria-expanded="true"] .chevron {{ transform: rotate(90deg); }}
  .draw-label {{ flex: 1; font-size: 12.5px; font-weight: 600; }}
  .draw-count {{
    font-size: 10.5px; color: var(--text-secondary); background: var(--grey-100); border-radius: 999px;
    padding: 1px 7px; font-variant-numeric: tabular-nums;
  }}

  .draw-body {{
    list-style: none; margin: 0; padding: 0;
    max-height: 0; overflow: hidden; transition: max-height 200ms cubic-bezier(0.16,1,0.3,1);
  }}
  .draw-body[data-open="true"] {{ max-height: 400px; }}
  .draw-body li a {{
    display: block; padding: 6px 10px 6px 30px; font-size: 12.5px;
    text-decoration: none; color: var(--text-secondary); border-radius: 12px; margin: 1px 4px;
    font-variant-numeric: tabular-nums;
  }}
  .draw-body li a:hover {{ background: var(--grey-100); }}
  .draw-body li a.active {{ background: var(--blue-500); color: var(--white); font-weight: 600; }}

  #more-btn {{
    width: calc(100% - 8px); margin: 8px 4px 0; padding: 9px;
    border: 1px dashed var(--grey-200); border-radius: 12px; background: none;
    font-size: 12px; color: var(--text-secondary); cursor: pointer;
  }}
  #more-btn:hover {{ background: var(--grey-100); border-style: solid; }}

  iframe {{ flex: 1; border: none; }}
</style>
<div class="layout">
  <header class="top-nav">
    <button class="menu-btn" id="menu-btn" type="button" aria-label="리포트 목록 열기" aria-expanded="false" aria-controls="sidebar">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="4" y1="7" x2="20" y2="7"/><line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="17" x2="20" y2="17"/></svg>
    </button>
    <span class="title-1">리포트</span>
  </header>
  <div class="layout-body">
    <div class="sidebar-backdrop" id="sidebar-backdrop"></div>
    <nav class="sidebar" id="sidebar">
      <h1>리포트</h1>
      <ul id="group-list">
{items}
      </ul>
{more_button}    </nav>
    <iframe id="viewer" title="선택한 회차 리포트" src="{latest_name}"></iframe>
  </div>
</div>
<script>
const sidebar = document.getElementById('sidebar');
const sidebarBackdrop = document.getElementById('sidebar-backdrop');
const menuBtn = document.getElementById('menu-btn');

function closeSidebar() {{
  sidebar.classList.remove('is-open');
  sidebarBackdrop.classList.remove('is-open');
  menuBtn.setAttribute('aria-expanded', 'false');
}}
menuBtn.addEventListener('click', () => {{
  const open = sidebar.classList.toggle('is-open');
  sidebarBackdrop.classList.toggle('is-open', open);
  menuBtn.setAttribute('aria-expanded', String(open));
}});
sidebarBackdrop.addEventListener('click', closeSidebar);

document.querySelectorAll('.draw-header').forEach(btn => {{
  btn.addEventListener('click', () => {{
    const open = btn.getAttribute('aria-expanded') === 'true';
    btn.setAttribute('aria-expanded', open ? 'false' : 'true');
    btn.nextElementSibling.setAttribute('data-open', open ? 'false' : 'true');
  }});
}});

document.querySelectorAll('.draw-body a').forEach(a => {{
  a.addEventListener('click', (e) => {{
    e.preventDefault();
    document.getElementById('viewer').src = a.dataset.src;
    document.querySelectorAll('.draw-body a').forEach(el => el.classList.remove('active'));
    a.classList.add('active');
    closeSidebar();
  }});
}});

const moreBtn = document.getElementById('more-btn');
if (moreBtn) {{
  moreBtn.addEventListener('click', () => {{
    document.querySelectorAll('.draw-group.is-hidden').forEach(el => el.classList.remove('is-hidden'));
    moreBtn.remove();
  }});
}}
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
