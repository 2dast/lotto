---
name: 로또 리포트
version: "1.0"
description: 로또 번호 자동 수집·예측·정확도 트래킹 결과를 보여주는 정적 리포트의 디자인 토큰
slug: lotto-report
category: data-report
last_updated: "2026-09-13"
created_at: "2026-09-13"
sources:
  - base-reference: toss-design-system (colors/typography/spacing/rounded/elevation/motion tokens)
lang: ko
colors:
  primary: "{colors.blue-500}"
  fill-brand: "{colors.blue-500}"
  fill-primary: "{colors.grey-900}"
  fill-secondary: "{colors.grey-100}"
  fill-weak: "{colors.grey-50}"
  fill-danger: "{colors.red-500}"
  fill-success: "{colors.green-500}"
  fill-warning: "{colors.orange-500}"
  text-primary: "{colors.grey-900}"
  text-secondary: "{colors.grey-700}"
  text-tertiary: "{colors.fg-tertiary}"
  text-placeholder: "{colors.fg-quaternary}"
  text-alt: "{colors.white}"
  text-brand: "{colors.blue-500}"
  text-danger: "{colors.red-500}"
  border-primary: "{colors.blue-500}"   # focused input
  border-secondary: "{colors.grey-200}"   # default divider
  border-strong: "{colors.grey-400}"
  border-subtle: "{colors.line-subtle}"
  overlay-scrim: "{colors.bg-overlay}"
  overlay-press: "{colors.press-overlay}"
  ## Brand
  blue-500: oklch(0.624 0.176 254)   # 카노니컬 강조색, 화면당 하나의 primary 액션
  blue-600: oklch(0.522 0.176 257)   # pressed 단계
  blue-700: oklch(0.476 0.174 259)   # pressed gradient stop
  blue-50: oklch(0.965 0.020 250)   # brand-weak background
  ## Greyscale
  grey-900: oklch(0.234 0.030 254)   # primary text, never pure black
  grey-800: oklch(0.342 0.030 253)
  grey-700: oklch(0.452 0.028 253)   # secondary text
  grey-600: oklch(0.555 0.022 253)
  grey-500: oklch(0.652 0.020 252)
  grey-400: oklch(0.752 0.016 251)   # disabled text, strong line
  grey-300: oklch(0.840 0.012 248)
  grey-200: oklch(0.913 0.008 247)   # default divider/border
  grey-150: oklch(0.918 0.007 247)
  grey-100: oklch(0.957 0.005 247)   # secondary surface
  grey-50: oklch(0.978 0.003 247)
  white: oklch(1.000 0.000 0)
  ## Number pool accents (당첨번호 구간 색 — 로또 공식 번호 구간 색상 준용)
  ball-yellow: oklch(0.853 0.156 86)   # 1-10
  ball-blue: oklch(0.624 0.176 254)   # 11-20
  ball-red: oklch(0.628 0.218 22)   # 21-30
  ball-grey: oklch(0.555 0.022 253)   # 31-40
  ball-green: oklch(0.493 0.143 154)   # 41-45
  ## Toss yellow & orange
  yellow-500: oklch(0.853 0.156 86)   # illustration / emoji body
  yellow-400: oklch(0.893 0.123 85)
  yellow-300: oklch(0.901 0.124 84)
  yellow-600: oklch(0.840 0.171 87)
  yellow-700: oklch(0.872 0.169 87)
  orange-500: oklch(0.748 0.183 56)   # semantic warning
  orange-400: oklch(0.828 0.108 52)
  orange-300: oklch(0.870 0.078 51)
  ## Illustration warms
  brown-900: oklch(0.359 0.083 39)
  brown-700: oklch(0.444 0.062 30)
  brown-500: oklch(0.535 0.073 39)
  brown-400: oklch(0.659 0.097 41)
  ## Semantic palette
  red-500: oklch(0.628 0.218 22)   # 위험/오류/미당첨
  red-600: oklch(0.626 0.216 22)
  green-500: oklch(0.493 0.143 154)   # 성공/적중
  navy-900: oklch(0.155 0.060 261)   # overlay 베이스
  ## Semantic alpha tokens
  fg-tertiary: oklch(0.155 0.060 261 / 0.58)   # 흐린 본문 텍스트
  fg-quaternary: oklch(0.155 0.060 261 / 0.28)   # placeholder
  line-subtle: oklch(0.000 0.000 0 / 0.08)   # 카드 보더
  bg-overlay: oklch(0.000 0.000 0 / 0.56)   # 시트 scrim
  press-overlay: oklch(0.000 0.000 0 / 0.26)   # pressed-state tint
typography:
  display-1:
    fontFamily: "\"Pretendard Variable\", Pretendard, -apple-system, BlinkMacSystemFont, \"Apple SD Gothic Neo\", \"Noto Sans KR\", Roboto, \"Helvetica Neue\", Arial, sans-serif"
    fontSize: 56px
    fontWeight: 700
    lineHeight: 1.30
    letterSpacing: -0.005em
  display-2:
    fontFamily: "\"Pretendard Variable\", Pretendard, -apple-system, BlinkMacSystemFont, \"Apple SD Gothic Neo\", \"Noto Sans KR\", Roboto, \"Helvetica Neue\", Arial, sans-serif"
    fontSize: 40px
    fontWeight: 700
    lineHeight: 1.20
    letterSpacing: -0.020em
  h1:
    fontFamily: "\"Pretendard Variable\", Pretendard, -apple-system, BlinkMacSystemFont, \"Apple SD Gothic Neo\", \"Noto Sans KR\", Roboto, \"Helvetica Neue\", Arial, sans-serif"
    fontSize: 28px
    fontWeight: 700
    lineHeight: 1.30
    letterSpacing: -0.020em
  h2:
    fontFamily: "\"Pretendard Variable\", Pretendard, -apple-system, BlinkMacSystemFont, \"Apple SD Gothic Neo\", \"Noto Sans KR\", Roboto, \"Helvetica Neue\", Arial, sans-serif"
    fontSize: 24px
    fontWeight: 700
    lineHeight: 1.30
    letterSpacing: -0.020em
  h3:
    fontFamily: "\"Pretendard Variable\", Pretendard, -apple-system, BlinkMacSystemFont, \"Apple SD Gothic Neo\", \"Noto Sans KR\", Roboto, \"Helvetica Neue\", Arial, sans-serif"
    fontSize: 20px
    fontWeight: 700
    lineHeight: 1.35
    letterSpacing: -0.015em
  h4:
    fontFamily: "\"Pretendard Variable\", Pretendard, -apple-system, BlinkMacSystemFont, \"Apple SD Gothic Neo\", \"Noto Sans KR\", Roboto, \"Helvetica Neue\", Arial, sans-serif"
    fontSize: 20px
    fontWeight: 700
    lineHeight: 1.35
    letterSpacing: -0.015em
  title-1:
    fontFamily: "\"Pretendard Variable\", Pretendard, -apple-system, BlinkMacSystemFont, \"Apple SD Gothic Neo\", \"Noto Sans KR\", Roboto, \"Helvetica Neue\", Arial, sans-serif"
    fontSize: 18px
    fontWeight: 600
    lineHeight: 1.45
    letterSpacing: -0.010em
  title-2:
    fontFamily: "\"Pretendard Variable\", Pretendard, -apple-system, BlinkMacSystemFont, \"Apple SD Gothic Neo\", \"Noto Sans KR\", Roboto, \"Helvetica Neue\", Arial, sans-serif"
    fontSize: 17px
    fontWeight: 600
    lineHeight: 1.45
    letterSpacing: -0.010em
  body-1:
    fontFamily: "\"Pretendard Variable\", Pretendard, -apple-system, BlinkMacSystemFont, \"Apple SD Gothic Neo\", \"Noto Sans KR\", Roboto, \"Helvetica Neue\", Arial, sans-serif"
    fontSize: 15px
    fontWeight: 400
    lineHeight: 1.50
    letterSpacing: -0.005em
  body-2:
    fontFamily: "\"Pretendard Variable\", Pretendard, -apple-system, BlinkMacSystemFont, \"Apple SD Gothic Neo\", \"Noto Sans KR\", Roboto, \"Helvetica Neue\", Arial, sans-serif"
    fontSize: 15px
    fontWeight: 400
    lineHeight: 1.50
    letterSpacing: -0.005em
  body-3:
    fontFamily: "\"Pretendard Variable\", Pretendard, -apple-system, BlinkMacSystemFont, \"Apple SD Gothic Neo\", \"Noto Sans KR\", Roboto, \"Helvetica Neue\", Arial, sans-serif"
    fontSize: 13px
    fontWeight: 400
    lineHeight: 1.50
    letterSpacing: 0em
  label-l:
    fontFamily: "\"Pretendard Variable\", Pretendard, -apple-system, BlinkMacSystemFont, \"Apple SD Gothic Neo\", \"Noto Sans KR\", Roboto, \"Helvetica Neue\", Arial, sans-serif"
    fontSize: 17px
    fontWeight: 700
    lineHeight: 1.25
    letterSpacing: -0.005em
  label-m:
    fontFamily: "\"Pretendard Variable\", Pretendard, -apple-system, BlinkMacSystemFont, \"Apple SD Gothic Neo\", \"Noto Sans KR\", Roboto, \"Helvetica Neue\", Arial, sans-serif"
    fontSize: 15px
    fontWeight: 600
    lineHeight: 1.25
    letterSpacing: -0.005em
  label-s:
    fontFamily: "\"Pretendard Variable\", Pretendard, -apple-system, BlinkMacSystemFont, \"Apple SD Gothic Neo\", \"Noto Sans KR\", Roboto, \"Helvetica Neue\", Arial, sans-serif"
    fontSize: 13px
    fontWeight: 600
    lineHeight: 1.25
    letterSpacing: 0em
  table-numeric:
    fontFamily: "\"Pretendard Variable\", Pretendard, -apple-system, BlinkMacSystemFont, \"Apple SD Gothic Neo\", \"Noto Sans KR\", Roboto, \"Helvetica Neue\", Arial, sans-serif"
    fontSize: 15px
    fontWeight: 400
    lineHeight: 1.50
    letterSpacing: 0em
    fontFeature: "tabular-nums"
  caption:
    fontFamily: "\"Pretendard Variable\", Pretendard, -apple-system, BlinkMacSystemFont, \"Apple SD Gothic Neo\", \"Noto Sans KR\", Roboto, \"Helvetica Neue\", Arial, sans-serif"
    fontSize: 12px
    fontWeight: 500
    lineHeight: 1.40
    letterSpacing: 0em
  caption-s:
    fontFamily: "\"Pretendard Variable\", Pretendard, -apple-system, BlinkMacSystemFont, \"Apple SD Gothic Neo\", \"Noto Sans KR\", Roboto, \"Helvetica Neue\", Arial, sans-serif"
    fontSize: 11px
    fontWeight: 500
    lineHeight: 1.40
    letterSpacing: 0em
spacing:
  space-1: 4px
  space-2: 8px
  space-3: 12px
  space-4: 16px
  space-5: 20px
  space-6: 24px
  space-7: 28px
  space-8: 32px
  space-10: 40px
  space-12: 48px
  space-16: 64px
  space-20: 80px
rounded:
  radius-xs: 4px   # 작은 배지
  radius-s: 8px   # 인라인 태그
  radius-m: 12px   # 카드, 입력
  radius-l: 14px   # 버튼(L)
  radius-xl: 16px   # 버튼(XL), 큰 카드
  radius-2xl: 20px   # 시트, 다이얼로그
  radius-3xl: 24px   # 큰 카드/섹션
  radius-4xl: 32px   # 히어로 블록
  radius-full: 999px   # pill, 번호 볼
elevation:
  shadow-1: "0 1px 2px oklch(0.155 0.060 261 / 0.04), 0 1px 1px oklch(0.155 0.060 261 / 0.04)"   # 메뉴
  shadow-2: "0 4px 12px oklch(0.155 0.060 261 / 0.06), 0 1px 2px oklch(0.155 0.060 261 / 0.04)"   # 툴팁
  shadow-3: "0 12px 32px oklch(0.155 0.060 261 / 0.10), 0 2px 6px oklch(0.155 0.060 261 / 0.06)"   # 다이얼로그
  shadow-toast: "0 8px 24px oklch(0.155 0.060 261 / 0.16)"   # 토스트
opacity:
  disabled-opacity: 0.30
dark:
  # prefers-color-scheme: dark 에서 뒤집는 role. 새 색을 만들지 않고 기존 신문/증권
  # 리포트 다크 무드(scripts/report_template.html)에서 이미 쓰던 값을 그대로 재사용한다.
  blue-500: "#6f8fb8"
  blue-50: "#24344a"
  grey-900: "#ecebe6"   # -> text-primary (라이트의 grey-900 자리를 대체)
  grey-700: "#b7b6ac"   # -> text-secondary
  grey-400: "#85847a"
  grey-200: "#35363a"   # -> border-secondary
  grey-100: "#232428"
  grey-50: "#1d1e21"
  white: "#16171a"   # -> 페이지/카드 배경
  red-500: "#d9736b"
  green-500: "#4fa688"
  shadow-1: "0 1px 2px rgba(0,0,0,0.30), 0 1px 1px rgba(0,0,0,0.20)"
---

# 로또 리포트 — design.md

> 로또 번호 자동 수집·예측·정확도 트래킹 파이프라인의 결과물을 보여주는 정적 리포트(README·`reports/index.html`)를 위한 디자인 규칙 문서. 별도 디자인 시스템을 새로 만들지 않고, 토스 디자인 시스템(TDS)의 컬러/타이포/spacing/rounded/elevation/motion **토큰 구조를 리소스로 재사용**하되, 화면 구성·컴포넌트 명칭·카피는 본 프로젝트(로또 회차 데이터 리포트)의 성격에 맞게 다시 정의한다.

## Brand & Style

이 프로젝트는 금융 슈퍼앱이 아니라 **매주 자동 갱신되는 통계 리포트**다. 사용자는 "회차 결과가 나왔을 때 예측이 얼마나 맞았는지, 다음 회차 추천 번호가 무엇인지"를 빠르게 확인하러 온다. 따라서 화면의 우선순위는 (1) 최신 회차 예측/정확도 요약을 최상단에, (2) 과거 트렌드는 아래로, (3) 장식은 최소화한다.

톤은 "재미로 보는 통계 리포트"에 맞춰 담백하고 절제된다 — 과장된 확신형 카피("적중 보장", "다음엔 진짜 나옵니다") 금지, README에 이미 명시된 문구("본 예측은 통계적 근거가 없으며 오락 목적입니다")의 톤을 유지한다. 종결어미는 해요체보다 **평서형 요약체**(리포트 특성상 "~함", "~됨"보다는 "~입니다/~했습니다" 수준의 간결한 서술)를 쓴다.

무드는 토스 톤을 그대로 가져온다 — **화이트 캔버스 + 단일 블루 강조색**, 공격적이지 않은 12~16px 라운드, 그림자는 카드 표면에서만 낮은 알파로 사용한다. 그라디언트·텍스처는 사용하지 않는다.

## Colors

기본 팔레트는 토스 토큰 값을 그대로 차용한다. 추가로 이 프로젝트 전용 토큰을 둔다:

- `{colors.ball-yellow/blue/red/grey/green}` — 로또 공식 번호 구간 색상(1-10/11-20/21-30/31-40/41-45)과 매핑되는 번호 볼 색. 실제 로또 공을 흉내 내지 않고, 원본 팔레트에서 대응 hue를 가져와 통일감을 유지한다.
- `{colors.fill-success}` (green-500) — 예측 적중 표시.
- `{colors.fill-danger}` (red-500) — 예측 미적중/오차 표시.

product-facing 색은 시맨틱 alias(`{colors.fill-brand}`, `{colors.text-primary}` 등)로만 호출하고, base 팔레트는 새 역할을 만들 때만 직접 참조한다.

## Typography

본문/UI 서체는 **Pretendard**(무료 한글 서체)로 통일한다 — 토스 문서가 언급하는 TPS 대체 서체이자, 본 프로젝트가 재배포 제약 없이 바로 쓸 수 있는 서체다. 리포트 특성상 실시간 강조 애니메이션은 없으므로 tabular/proportional 숫자 구분만 가져온다:

- 회차 번호·정확도(%)·당첨금 등 **표 안 숫자는 tabular-nums** 고정폭.
- 본문 강조 숫자(예: "이번 주 3개 적중")는 proportional-nums.

타입 램프는 h1(28/700, 리포트 타이틀) → h2(24/700, 섹션 제목) → h3(20/700, 카드 제목) → title-1(18/600, 회차 라벨) → body-1(15/400, 본문) → label-m(15/600, 배지/버튼 라벨) → caption(12/500, 각주·업데이트 시각)로 축소했다.

## Layout & Spacing

토스 토큰의 작은~중간 구간(4~64px, 라운드 4~16px + full)만 가져온다 — 리포트는 hero 블록·bottom sheet 같은 대형 모바일 컴포넌트가 없으므로 32px 이상 라운드, 80px 이상 spacing은 이 프로젝트 범위에서 제외한다.

- 화면 outer padding: **24px**
- 카드 간 간격: **16px**
- 라벨-값 밀접 쌍: **8px**
- 카드/입력 라운드: **12px**, 큰 카드: **16px**, 번호 볼/배지: **full**

## Elevation & Depth

카드 표면에만 낮은 알파 그림자를 쓴다(토스 `shadow-1`/`shadow-2`와 동일한 navy-900 기반 저알파 값). 모션은 정적 리포트 특성상 최소화한다 — hover/toggle 전환에만 `dur-base` 200ms `ease-out-expo`를 쓰고, 그 외 애니메이션(로딩 스피너, 시트 전환 등)은 이 프로젝트에 해당 UI가 없으므로 정의하지 않는다.

## Shapes

기하학은 **평면 표면 + 헤어라인 보더 + 절제된 라운드**로 요약된다. 기본 보더는 1px `{colors.border-secondary}` 헤어라인이며, 2px 이상 장식용 보더나 컬러 accent 카드는 쓰지 않는다. 카드 라운드는 `{rounded.radius-m}`(12)~`{rounded.radius-xl}`(16)로 고정하고, 번호 볼·배지류만 `{rounded.radius-full}`(pill)을 쓴다. 그림자는 `Elevation & Depth`에서 정의한 저알파 카드 그림자 외에 별도 장식 그림자를 두지 않는다.

## Components

정적 HTML 리포트(`scripts/report_template.html`, `reports/index.html`)에서 실제로 쓰이는 단위만 정의한다.

### summary-card

리포트 최상단 요약 카드 — `{rounded.radius-xl}` (16), 1px `{colors.border-secondary}` 헤어라인, `{elevation.shadow-1}`. 제목은 `title-1`, 핵심 지표(적중 개수 등)는 `h2` + tabular-nums.

### number-ball

회차 번호를 표시하는 원형 배지 — `{rounded.radius-full}`, 32~40px, 배경은 번호 구간별 `{colors.ball-*}` + 흰 텍스트(`label-m`, Bold). 예측 번호와 실제 당첨 번호를 시각적으로 구분할 때, 적중 번호에는 2px `{colors.fill-success}` 외곽선을 추가한다.

```html
<span class="number-ball ball-blue">14</span>
<span class="number-ball ball-red hit">23</span>
```

### accuracy-badge

예측 정확도(적중 개수)를 나타내는 pill — `{rounded.radius-full}`, `{colors.blue-50}` 배경 + `{colors.text-brand}` 텍스트(`label-m`). 0개 적중은 `{colors.fill-secondary}` + `{colors.text-secondary}`로 톤 다운한다.

### track-row

`scripts/track_accuracy.py` 결과를 한 줄로 보여주는 표 행 — 회차/예측 세트/적중 개수/생성 시각 4열, 1px `{colors.border-secondary}` 헤어라인으로 행 구분. 수치 열은 tabular-nums, 우측 정렬.

### trend-chart

`scripts/build_dashboard.py`가 생성하는 회차별 적중 추이 막대 그래프 — 막대는 기본 `{colors.grey-200}`, 최고 적중 회차만 `{colors.fill-brand}`로 강조. axis line·divider는 두지 않고 막대만 표면 위에 띄운다(토스 bar-chart 규칙 유지).

### footnote

"본 예측은 통계적 근거가 없으며 오락 목적입니다" 같은 면책 문구 — `caption`(12/500) + `{colors.text-tertiary}`.

### button

대시보드/일반 페이지에서 쓰는 클릭 액션. 우리 라운드 사다리(4/8/12/14/16/full)에 맞춰 **L/M/S** 3단만 둔다 — XL(56px)은 정적 리포트·대시보드 어디에도 전체화면 CTA가 없으므로 제외한다.

| 사이즈 | height | radius | label |
|---|---|---|---|
| L | 48 | `{rounded.radius-l}` (14) | `label-m` (15px Semibold) |
| M | 40 | `{rounded.radius-m}` (12) | `label-m` (15px Semibold) |
| S | 32 | `{rounded.radius-s}` (8)  | `caption` (12px Semibold) |

- **primary**: `{colors.fill-brand}` 배경 + `{colors.text-alt}` 텍스트. 화면당 하나의 주요 액션(예: "최신 회차 보기")에만 사용.
- **secondary**: `{colors.fill-secondary}` 배경 + `{colors.text-primary}` 텍스트. 보조 액션(예: "이전 회차").
- **pressed**: `{colors.overlay-press}`(검정 26%)를 배경 위에 얹는다 — 별도 색을 만들지 않는다.
- **disabled**: 컴포넌트 전체에 `{opacity.disabled-opacity}`(0.30) 적용, 부분 회색 처리 금지.

```html
<button class="btn btn-primary btn-m">최신 회차 보기</button>
<button class="btn btn-secondary btn-s">이전 회차</button>
```

### top-nav

일반 페이지/대시보드 상단 고정 바 — 56px 높이, 좌측 타이틀(`title-1`), 우측에 `button`(S) 슬롯. 배경은 `{colors.white}`, 하단 보더는 1px `{colors.border-secondary}` 헤어라인(그림자 없음 — `Shapes` 규칙과 동일하게 평면 유지).

### filter-chip

대시보드에서 회차 범위·번호 구간 등을 고르는 토글형 칩 — 32px 높이, `{rounded.radius-full}`. resting은 1px `{colors.border-secondary}` + 흰 배경, active는 `{colors.blue-50}` 배경 + `{colors.text-brand}` 텍스트(`caption`, Semibold). 여러 개 동시 선택 가능(다중 선택), 단일 선택이 필요하면 `segmented-control`처럼 별도 컴포넌트로 분리한다(현재 프로젝트엔 아직 없음).

## Do's and Don'ts

**Do**

- product-facing 색은 시맨틱 alias로만 호출한다.
- 화면당 단일 강조색(`{colors.fill-brand}`) 정책을 유지한다.
- 회차 번호·정확도·업데이트 시각 등 표 안 수치는 tabular-nums로 통일한다.
- 예측 적중/미적중은 색(`{colors.fill-success}`/`{colors.fill-danger}`)으로만 구분하고 아이콘을 과하게 쓰지 않는다.
- 면책 문구(오락 목적 안내)는 항상 `footnote` 스타일로 유지한다.

**Don't**

- "적중 보장", "다음엔 확실합니다" 같은 과장 카피를 쓰지 않는다 — 로또는 완전 무작위 추첨이라는 README의 전제와 모순된다.
- 그라디언트·텍스처·전면 사진을 chrome에 사용하지 않는다.
- 32px 이상 라운드, 80px 이상 spacing 등 이 프로젝트 범위 밖의 토스 대형 토큰을 끌어오지 않는다 — 정적 리포트에는 hero/bottom-sheet급 레이아웃이 없다.
- 한 화면에 강조색을 둘 이상 쓰지 않는다.
- 대시보드/일반 페이지에도 XL(56px) 버튼이나 bottom-sheet급 오버레이를 새로 들여오지 않는다 — 이 프로젝트는 `button`(L/M/S)과 `top-nav`, `filter-chip`만으로 화면을 구성한다.

## Dark Mode

`prefers-color-scheme: dark`로 자동 전환한다(별도 토글 UI는 두지 않음). 새 다크 팔레트를 만들지 않고, `scripts/report_template.html`이 이미 쓰던 신문/증권 리포트 무드의 다크 값을 `{dark.*}` alias로 그대로 재사용해서 대시보드·리포트 목록·개별 리포트 세 화면이 같은 톤으로 맞춰진다.

- 역할 매핑은 라이트와 동일한 이름을 유지한 채 값만 바뀐다: `{colors.text-primary}`(grey-900 역할)는 다크에서 `{dark.grey-900}`(#ecebe6), `{colors.fill-brand}`(blue-500)는 `{dark.blue-500}`(#6f8fb8, 어두운 배경에서 채도를 낮춘 네이비-블루)로 대체.
- 카드 그림자(`{elevation.shadow-1}`)는 다크에서 알파를 낮은 흰색이 아니라 더 짙은 검정(`{dark.shadow-1}`)으로 바꿔 낮은 대비를 유지한다.
- `number-ball.ball-yellow`처럼 배경색 자체가 밝은 색(옐로)인 컴포넌트는 라이트/다크와 무관하게 텍스트를 항상 짙은 색으로 고정한다 — 대비 확보가 role alias보다 우선.
- 적용 대상은 이 프로젝트의 모든 정적 페이지(`index.html` 대시보드, `reports/index.html` 리포트 목록, `scripts/report_template.html`이 생성하는 개별 리포트)다.

## Responsive Behavior

리포트·대시보드·일반 페이지 모두 **데스크톱/모바일 겸용 단일 컬럼** 기준으로 둔다. 별도 breakpoint 토큰 표는 두지 않고, 아래 원칙만 따른다.

- **Mobile (≤ 640px)**: `{component.top-nav}`는 그대로 고정, `filter-chip` 목록은 가로 스크롤. 카드(`summary-card`, `trend-chart`)는 1열.
- **Desktop (> 640px)**: 카드가 2열 그리드로 확장될 수 있으나, `number-ball`·`track-row` 등 표 형태 컴포넌트는 계속 단일 컬럼(가독성 우선).
- **Touch target**: 모든 `button`·`filter-chip`은 최소 32px 높이를 유지해 터치 오차를 줄인다.

## Known Gaps

- **폰트 라이선스** — Pretendard는 오픈 라이선스이므로 재배포 문제 없음(토스 TPS와 달리 substitute 불필요).
