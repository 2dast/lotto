# 프로젝트 웹 표준 가이드

정적 HTML 리포트/대시보드(`scripts/report_template.html`, `scripts/build_index.py`,
`scripts/build_dashboard.py`가 생성하는 `index.html`, `reports/*.html`)를 다룰 때
따르는 기준. `design.md`가 디자인 토큰을 정의하듯, 이 문서는 코드 품질/표준을 정의한다.
지금 이 문서를 적용해 기존 코드를 일괄 수정하지는 않는다 — 앞으로의 작업에 적용되는 기준이다.

## HTML

- 시맨틱 태그 우선: `<nav>`, `<section>`, `<table>`/`<thead>`/`<tbody>`, `<button>`을
  div/span 남용 대신 사용한다 (지금 accordion의 `<button class="draw-header">`가 좋은 예).
- 모든 비-void 요소는 닫는다. 속성은 큰따옴표로 통일한다.
- `<title>`은 모든 페이지에 필수.

## 접근성 (a11y)

- 토글/아코디언 등 상태가 바뀌는 컨트롤은 `aria-expanded` 등 ARIA 상태 속성을 실제 상태와
  동기화한다 (지금 `.draw-header[aria-expanded]` 패턴 유지).
- 키보드 포커스 상태를 지우지 않는다 — `outline: none`만 걸고 대체 포커스 스타일 없이 끝내지 않는다.
- 색만으로 의미를 구분하지 않는다 (예: 통과/미달을 색 대신 텍스트로도 표기).
- 이미지/아이콘에 의미가 있으면 대체 텍스트를 제공한다.

## 반응형 / 레이아웃 (모바일 필수)

- 이 프로젝트의 정적 페이지는 **데스크톱과 모바일 둘 다 지원한다.** 새 화면/컴포넌트를
  추가할 때 768px 이하 폭에서 실제로 확인한다(브라우저 개발자도구 반응형 모드 등).
- **좌측 고정 사이드바 레이아웃**(`index.html`, `reports/index.html`)은 768px 이하에서
  오프캔버스 드로어로 전환한다: 사이드바는 `position: fixed` + `transform: translateX`로
  숨겨두고, 상단바의 햄버거 버튼(`aria-expanded` 동기화)으로 열고 닫는다. 배경 클릭이나
  항목 선택 시 자동으로 닫는다. 이 패턴은 이미 `scripts/build_dashboard.py`,
  `scripts/build_index.py`에 구현되어 있으니 새 사이드바 UI는 그대로 재사용한다.
- 어떤 경우에도 **가로 스크롤이 body 레벨에서 강제로 발생하면 안 된다** — 표는
  `.table-scroll`(`overflow-x: auto`)로 감싸고, 카드/그리드는 `flex-wrap`/미디어쿼리로
  좁은 폭에 대응한다.
- `flex`/`grid` + `gap` 사용을 우선하고, 마진으로 간격을 흉내내지 않는다.
- 숫자가 컬럼으로 줄지어 나오는 곳(회차, 합계, 홀짝 등)은 `font-variant-numeric: tabular-nums`.
- iframe에는 접근성을 위해 `title` 속성을 항상 붙인다 (예: `title="선택한 회차 리포트"`).

## 다크모드

- 새 페이지/컴포넌트는 `prefers-color-scheme: dark`와 `data-theme` 오버라이드를 함께 고려한다.
  (`report_template.html`이 이미 이 패턴을 씀 — 새 화면도 라이트 전용으로 고정하지 않는다.)
- 색상은 CSS 커스텀 프로퍼티(토큰)로 선언하고, 다크 모드에서 값만 갈아끼운다.

## 성능

- 무거운 프레임워크(React/Vue 등)를 정적 리포트에 들여오지 않는다 — 바닐라 JS로 충분한 규모.
- 외부 스크립트는 필요한 것만, 신뢰 가능한 CDN(Pretendard, Google Fonts 등)에서 pin된 버전으로.
- 리포트 1개당 데이터 양(예측 5세트, 회차 목록)은 작으므로 가상 스크롤 등 최적화는 불필요 —
  과도한 엔지니어링을 하지 않는다.

## 보안

- 생성 스크립트가 만드는 HTML에 사용자 입력이 직접 삽입되는 지점이 없는지 확인한다
  (지금은 전부 내부 데이터(JSON)만 다루므로 XSS 위험 낮음 — 외부 입력을 다루게 되면 이스케이프 필수).
- 인라인 이벤트 핸들러(`onclick="..."`) 대신 `addEventListener`를 쓴다 (지금 패턴 유지).

## 브라우저 호환

- 최신 2개 메이저 버전의 Chrome/Edge/Safari/Firefox를 기준으로 한다 — GitHub Pages로
  배포되는 공개 정적 사이트이므로 구형 브라우저 폴리필은 하지 않는다.
- 실험적/비표준 CSS(`@supports` 없이 최신 API만 의존)는 피한다.
