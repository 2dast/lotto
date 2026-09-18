# Astro 기반 동적 웹 재구축

## Problem

- 현재 로또 예측 대시보드/리포트는 Python 스크립트(`build_dashboard.py`, `build_index.py`,
  `generate_report.py`)가 생성하는 정적 HTML이다.
- 모바일 가로 스크롤·터치 타겟 문제는 이미 CSS 수정으로 해결됐지만, 사용자는 장기적으로
  스택을 현대화하고(Astro 기반) 계산 로직(예측 생성, 데이터 수집)까지 TypeScript로
  이전하기를 원한다.
- 이 문제는 프로젝트 소유자(1인 개발자)만 겪으며, 오늘날은 Python 파이프라인 +
  GitHub Actions로 매주 자동 갱신하는 방식으로 해결하고 있다.

## Scope

**In scope**
- `scripts/predict.py`, `scripts/collect.py`의 로직을 TypeScript로 이식
- 대시보드(`index.html`), 리포트 목록(`reports/index.html`), 리포트 상세
  (`reports/round_*/*.html`) 3개 화면을 Astro로 재구축
- Astro Content Layer(커스텀 loader)로 수집·예측을 `astro build` 실행 시 자동 수행
- GitHub Actions 워크플로우를 Node/Astro 기반으로 교체

**Out of scope**
- `scripts/analyze_recent_patterns.py` — 사이트/빌드에 쓰이지 않는 개발자용 분석 CLI, 이번 마이그레이션 대상 아님
- 사용자 계정, 서버 사이드 동적 계산, DB 저장 — 서버 없는 SSG로 유지
- `data/draws.json`, `predictions/*.json`의 데이터 마이그레이션 — 포맷 불변이라 필요 없음

## User Stories

- **US-1**: 사용자로서, 대시보드(`/`)에서 최신 회차 예측을 모바일에서도 가로 스크롤 없이 확인하고 싶다.
  - Given 375px~1440px 사이 임의의 뷰포트, When 대시보드에 접속하면, Then 카드가 뷰포트 폭에 맞게 재배치되고 가로 스크롤이 없다.
  - Priority: must
- **US-2**: 사용자로서, 과거에 생성된 회차별 예측 파일을 드롭다운으로 선택해서 비교하고 싶다. (기존 기능 유지)
  - Given 특정 회차, When select에서 다른 타임스탬프 파일을 선택하면, Then 해당 예측 데이터로 화면이 갱신된다.
  - Priority: must
- **US-3**: 사용자로서, 리포트 목록(`/reports`)에서 회차별 리포트 이력을 탐색하고 싶다. (기존 기능 유지)
  - Priority: must
- **US-4**: 사용자로서, 리포트 상세 페이지에서 예측 세트별 홀짝/구간/분포 분석을 보고 싶다. (기존 JS 로직 그대로)
  - Priority: must
- **US-5**: 운영자(나)로서, GitHub Actions가 매주 토요일 자동으로 최신 회차를 수집하고 예측을 생성해 사이트를 갱신하길 원한다.
  - Given 매주 토요일 21:10 KST 또는 수동 트리거, When 워크플로우가 실행되면, Then `astro build`가 최신 데이터로 정적 사이트를 재생성하고 커밋한다.
  - Priority: must
- **US-6**: 운영자로서, 예측 생성 로직(필터링·점수화)이 Python 버전과 동일한 결과를 내는지 확인하고 싶다.
  - Given 동일한 `data/draws.json`과 RULES, When 결정적 로직(필터/점수 계산)을 실행하면, Then Python 테스트 케이스와 동일한 pass/fail 결과가 나온다. 단, 가중 랜덤 추출 자체는 RNG 차이로 정확히 같은 수를 재현하지 않으므로 분포 검증만 한다.
  - Priority: must

## Constraints

- 서버 없는 정적 호스팅(GitHub Pages) 유지 — SSG만 허용, 런타임 백엔드 불가
- 동행복권 비공식 내부 API는 브라우저에서 직접 호출 시 CORS로 막히므로 반드시 빌드타임에만 호출
- `data/draws.json`, `predictions/*.json` 파일 포맷은 하위 호환 유지 (기존 이력 파일 재사용)
- `RULES.md`, `RULES_2.md`의 DSL 문법은 변경하지 않음
- `design.md`(디자인 토큰), `CLAUDE.md`(웹 표준)의 기존 기준은 Astro 컴포넌트에도 계속 적용

## Context

### 현재 동작 (Python 파이프라인)

1. `collect.py` — 동행복권 내부 API(`selectPstLt645InfoNew.do`)를 `requests`로 호출해
   `data/draws.json`에 누적 저장. `srchDir=older`(페이지네이션)와 `srchDir=center`(최신 회차
   포함 조회) 두 엔드포인트를 함께 사용.
2. `predict.py` — `RULES.md`/`RULES_2.md`를 정규식 기반 커스텀 DSL로 파싱, `score_numbers`로
   전체/최근 빈도 가중 점수 계산, `passes_filters`(홀짝/합계/연속/구간)로 후보를 거르고
   `random.choices` 가중 랜덤으로 5세트씩 추출. 결과를
   `predictions/round_{n}/predictions_{n}_{timestamp}.json`에 저장.
3. `generate_report.py` — 최신 예측 JSON을 `report_template.html`에 문자열 치환으로 삽입해
   `reports/round_{n}/lotto_report_{n}_{timestamp}.html` 생성.
4. `build_index.py`, `build_dashboard.py` — 리포트 목록/대시보드 HTML을 생성.
5. GitHub Actions(`lotto.yml`)가 매주 토요일 위 순서로 전부 실행 후 결과를 자동 커밋·푸시.

### 재사용 가능한 기존 자산

- `report_template.html`의 표/차트 렌더링(`renderPredTable`, `renderRangeCharts`,
  `renderDistribution`, `officialColor` 등)은 **이미 클라이언트 사이드 JS**다. Python은
  예측 JSON을 템플릿에 끼워넣기만 한다 — 이 렌더링 로직은 재작성 없이 Astro 컴포넌트로
  그대로 옮길 수 있다.
- `tests/test_predict.py`는 `passes_filters` 같은 결정적 로직만 테스트한다 — 랜덤 추출은
  테스트 대상이 아니었으므로, TS 이식 후에도 같은 기준(결정적 로직 일치)으로 검증 가능.

### 알아둘 것 (Gotchas)

- `predict.py`의 예측 생성은 **비결정적**이다 (`random.choices`). Python↔TS 간 완전히
  동일한 난수 시퀀스를 기대할 수 없다.
- `predictions/round_1242/`에는 이미 18개 이상의 타임스탬프 파일이 쌓여있다 — 파일명
  규칙(`predictions_{round}_{yyyyMMdd}_{HHmmss}.json`)을 그대로 유지해야 기존 이력과
  섞여도 문제없다.
- `generate_report.py`의 `load_latest_predictions`는 파일명이 아니라 `generated_at`
  필드(ISO8601)로 최신 파일을 정렬한다 — 파일명 순 정렬은 zero-padding이 없어 신뢰할 수
  없다는 주석이 있음. TS 이식 시 이 정렬 기준을 반드시 유지해야 한다.

## Architecture

### 컴포넌트 구조

```
astro-app/
├── src/
│   ├── lib/lotto/                    ← 순수 로직 (함수형 코어, IO 없음)
│   │   ├── rules.ts                  # RULES.md 파서 (parseRuleLines, loadRules)
│   │   ├── score.ts                  # scoreNumbers (빈도 가중치 계산)
│   │   ├── filters.ts                # passesFilters (홀짝/합계/연속/구간)
│   │   └── generate.ts               # weightedSample, generateCombo, generatePredictions
│   ├── content/
│   │   └── loaders/
│   │       ├── draws-loader.ts       ← 이펙트풀 엣지: 동행복권 내부 API fetch
│   │       └── predictions-loader.ts ← 이펙트풀 엣지: lib/lotto 호출해 예측 생성·저장
│   ├── content.config.ts             ← Astro Content Layer: draws, predictions 컬렉션 정의
│   ├── pages/
│   │   ├── index.astro               # 대시보드
│   │   └── reports/
│   │       ├── index.astro           # 리포트 목록
│   │       └── [round]/[file].astro  # 리포트 상세 (동적 라우트)
│   └── components/
│       ├── PredictionTable.astro     # renderPredTable 이식
│       ├── RangeChart.astro          # renderRangeCharts 이식
│       └── DistributionChart.astro   # renderDistribution 이식
├── data/draws.json                   ← 그대로 유지 (커밋되는 영속 데이터)
└── predictions/round_*/*.json        ← 그대로 유지
```

### 도메인 모델

- **Draw**: `{ drwNo: number, numbers: number[], date: string }`
- **Rules**: `{ frequency: {...}, pattern_filters: {...}, num_predictions: number, exclude_numbers: number[], include_numbers: number[] }`
- **PredictionSet**: `{ based_on_drwNo: number, generated_at: string, option1: { predictions: number[][] }, option2: {...} | null }`

### 비즈니스 로직 vs IO 경계

- `src/lib/lotto/*`는 순수 함수만 포함 — 입력(draws, rules) → 출력(scores, predictions),
  파일/네트워크 접근 없음. Python 버전과 동일 결과를 내는지 유닛테스트로 검증하는 대상.
- `src/content/loaders/*`가 유일한 IO 지점 — 외부 API 호출(`draws-loader.ts`), 파일
  읽기/쓰기(`predictions-loader.ts`). Astro Content Layer API를 통해 `astro build` 실행
  시 자동으로 호출됨.
- 페이지(`*.astro`)는 `getCollection('draws')`, `getCollection('predictions')`로 이미
  로드된 데이터만 읽고 렌더링 — 로직 없음.

### 빌드 실패 처리

- `draws-loader.ts`에서 외부 API fetch 실패 시 예외로 빌드를 중단시키지 않고, 콘솔 경고 후
  커밋된 기존 `data/draws.json`을 그대로 사용해 빌드를 계속 진행한다. 별도 재시도 로직은
  만들지 않는다 — 다음 스케줄 실행 때 다시 시도된다.

## API Design

해당 없음 — 서버가 없는 정적 사이트(SSG)라 사용자에게 노출되는 런타임 API가 없다.

### 외부 API 계약 (동행복권 내부 API, `draws-loader.ts`가 소비)

```
GET https://www.dhlottery.co.kr/lt645/selectPstLt645InfoNew.do
  ?srchDir=older&srchCursorLtEpsd={cursor}   (과거 회차 페이지네이션, 10개씩)
  ?srchDir=center&srchLtEpsd={epsd}          (특정 회차 중심 조회, 최신 회차 포함)
Headers: User-Agent, X-Requested-With: XMLHttpRequest
Response: { data: { list: [...] } }
```

collect.py와 동일한 요청 형식을 그대로 유지한다 (비공식 API라 임의로 바꾸면 안 된다).

## Data Model

### Astro Content Layer

```ts
// content.config.ts
const draws = defineCollection({
  loader: drawsLoader(),
  schema: z.object({
    drwNo: z.number(),
    numbers: z.array(z.number()).length(6),
    date: z.string(),
  }),
});

const predictions = defineCollection({
  loader: predictionsLoader(),
  schema: z.object({
    based_on_drwNo: z.number(),
    generated_at: z.string(),
    option1: z.object({ predictions: z.array(z.array(z.number())) }),
    option2: z.object({ predictions: z.array(z.array(z.number())) }).nullable(),
  }),
});
```

### 파일 데이터 모델 (변경 없음)

- `data/draws.json`: `Draw[]` — 기존 포맷 그대로
- `predictions/round_{n}/predictions_{n}_{timestamp}.json`: `PredictionSet` — 기존
  포맷/네이밍 그대로 (기존 이력 파일들과 호환 유지)

마이그레이션 스크립트는 필요 없다 — 기존 JSON 파일을 Content Layer가 그대로 읽는다.

## Trade-offs

- **B안(Astro 빌드 훅에 수집·예측 통합)을 선택**했다 — 명령 하나(`astro build`)로 전체
  파이프라인이 실행되는 대신, 외부 API 장애 시 빌드가 오래된 데이터로 조용히 넘어갈 수
  있다(콘솔 경고만 남음). 각 단계를 독립적으로 재시도할 수 있었던 기존 Python 파이프라인의
  장점을 일부 잃는다. 사용자가 이 트레이드오프를 인지하고 "오류는 발생하면 그때 고친다"는
  전제로 승인했다.
- 가중 랜덤 추출은 Python `random`과 JS `Math.random` 기반 알고리즘이 달라 완전히 동일한
  예측 숫자를 재현하지 못한다 — 결정적 로직(필터/점수)만 동일성 검증, 랜덤 추출은 분포로만
  검증한다.
- 기존 `predictions/round_1242/*.json` 등 이력 파일은 Python으로 생성됐고 앞으로는 TS로
  생성되지만, 파일 포맷이 동일하므로 같은 디렉터리에 섞여도 문제없다.

## Known Limitations

- `scripts/analyze_recent_patterns.py`는 이번 마이그레이션에서 다루지 않는다 — 사이트/빌드
  파이프라인에 쓰이지 않는 개발자용 분석 CLI이기 때문이다. 필요해지면 별도 스펙으로 다룬다.
- 빌드 실패 시 재시도·알림 로직은 만들지 않는다(과설계 방지) — 다음 스케줄 실행에 의존한다.

## Open Questions

없음 — 논의 과정에서 모두 해소됨.
