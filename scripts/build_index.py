"""reports/round_<회차>/ 안의 lotto_report_<회차>_<timestamp>.html 파일들을 스캔해서
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
FILENAME_RE = re.compile(r"^lotto_report_(\d+)_(\d{8})_(\d{6})\.html$")
VISIBLE_GROUPS = 10


def list_reports():
    """(next_draw, timestamp, "round_<회차>/<파일명>") 튜플 리스트를 반환한다."""
    reports = []
    for path in REPORT_DIR.glob("round_*/lotto_report_*.html"):
        m = FILENAME_RE.match(path.name)
        if not m:
            continue
        next_draw = int(m.group(1))
        timestamp = dt.datetime.strptime(m.group(2) + m.group(3), "%Y%m%d%H%M%S")
        rel_path = f"{path.parent.name}/{path.name}"
        reports.append((next_draw, timestamp, rel_path))
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

    theme_toggle_svg = """<svg class="icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
      <svg class="icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>"""

    return f"""<title>로또 분석 리포트</title>
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
    --text-primary: var(--grey-900);
    --text-secondary: var(--grey-700);
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
    --shadow-1: 0 1px 2px rgba(0, 0, 0, 0.30), 0 1px 1px rgba(0, 0, 0, 0.20);
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; color: var(--text-primary); background: var(--white);
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

  .layout {{ display: flex; height: 100vh; flex-direction: column; }}
  .layout-body {{ display: flex; flex: 1; min-height: 0; }}
  .sidebar {{ width: 260px; flex: none; overflow-y: auto; border-right: 1px solid var(--border-secondary); background: var(--grey-50); }}
  .sidebar h1 {{
    height: 56px; display: flex; align-items: center; justify-content: space-between;
    font-size: 18px; font-weight: 600; letter-spacing: -0.01em; padding: 0 8px 0 16px; margin: 0;
    border-bottom: 1px solid var(--border-secondary);
  }}
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
    <span class="title-1" style="flex:1">리포트</span>
    <button class="theme-btn" id="theme-btn-mobile" type="button" aria-label="다크 모드 전환">
      {theme_toggle_svg}
    </button>
  </header>
  <div class="layout-body">
    <div class="sidebar-backdrop" id="sidebar-backdrop"></div>
    <nav class="sidebar" id="sidebar">
      <h1>
        <span>리포트</span>
        <button class="theme-btn" id="theme-btn-desktop" type="button" aria-label="다크 모드 전환">
          {theme_toggle_svg}
        </button>
      </h1>
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
const viewer = document.getElementById('viewer');

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
function toggleTheme() {{
  const next = currentTheme() === 'dark' ? 'light' : 'dark';
  document.documentElement.dataset.theme = next;
  try {{ localStorage.setItem('lotto-theme', next); }} catch (e) {{}}
  syncIframeTheme();
}}
document.getElementById('theme-btn-desktop').addEventListener('click', toggleTheme);
document.getElementById('theme-btn-mobile').addEventListener('click', toggleTheme);
viewer.addEventListener('load', syncIframeTheme);

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
