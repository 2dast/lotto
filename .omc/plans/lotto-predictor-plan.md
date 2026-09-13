# 로또번호 예측기 — 작업 계획 (pending approval)

## Requirements Summary

- GitHub Actions(무료 티어)로 매주 토요일 추첨 직후 1회 실행되는 자동 파이프라인 구축
- 회차별 당첨번호 데이터를 저장소 내부 파일(JSON)에 누적 저장 (별도 DB 없음)
- "빈도 + 패턴 조합" 기준으로 예측 번호 세트 생성
  - 빈도: 전체 출현 빈도, 최근 N회 출현 빈도(가중치 부여)
  - 패턴: 홀짝 비율, 구간(1-9/10-19/.../40-45) 분포, 연속번호 제한, 총합 범위 필터
- 예측 결과를 README.md에 자동 반영 (커밋)
- 언어: Python
- 데이터 출처: 동행복권 비공식 JSON 엔드포인트 `getLottoNumber` (HTML 크롤링 대신 — 더 단순하고 안정적)

## 범위 밖 (Out of Scope)

- 실제 당첨 예측의 통계적 유효성 보장 (로또는 완전 무작위이므로 예측은 참고용 오락 목적임을 README에 명시)
- 유료 DB, 알림(텔레그램/이메일) 연동 — 필요 시 추후 별도 요청

---

## Acceptance Criteria

1. `scripts/collect.py` 실행 시 `data/draws.json`에 없는 회차만 API에서 가져와 추가된다 (중복 없음, `pytest tests/test_collect.py` 통과)
2. `scripts/predict.py` 실행 시 `data/draws.json`을 읽어 6개 번호 조합을 N세트(기본 5세트) 생성하고, 각 조합이 패턴 필터(홀짝 2~4개, 구간당 최대 3개, 연속번호 최대 2개, 총합 100~170)를 통과한다 (`pytest tests/test_predict.py` 통과)
3. `README.md`의 `<!-- PREDICTION:START -->` ~ `<!-- PREDICTION:END -->` 마커 사이 내용이 최신 예측 결과와 생성 일시로 교체된다
4. `.github/workflows/lotto.yml`이 매주 토요일 21:10 KST(12:10 UTC) cron으로 실행되고, `workflow_dispatch`로 수동 실행도 가능하다
5. Actions 실행 시 `GITHUB_TOKEN` 기본 권한만으로 `data/draws.json`, `README.md` 변경사항을 자동 커밋한다
6. 신규 회차 데이터가 아직 발표 전이면(API 응답 없음) 워크플로우가 에러 없이 스킵하고 로그만 남긴다

---

## Implementation Steps

1. **저장소 기본 구조 생성** → 검증: `git status`로 파일 트리 확인
   - `requirements.txt` (requests, 표준 라이브러리 위주로 최소화)
   - `data/draws.json` (초기값 `[]` 또는 1회차부터 백필)
   - `README.md` 초안 + 예측 마커 삽입

2. **`scripts/collect.py` 작성** → 검증: `python scripts/collect.py` 로컬 실행 후 `data/draws.json`에 신규 회차 추가 확인
   - `data/draws.json`에서 마지막 회차 번호 확인
   - `https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={n}` 순차 호출 (returnValue: fail 이면 중단)
   - 각 회차: `{drwNo, date, numbers[6], bonusNo}` 저장

3. **`scripts/predict.py` 작성** → 검증: `pytest tests/test_predict.py`
   - 번호별 전체 빈도 + 최근 20회 빈도 계산, 가중합 점수화
   - 점수 상위 번호 풀에서 조합 샘플링 → 패턴 필터(홀짝/구간/연속/총합) 통과 조합만 채택
   - 통과 조합 5세트를 `predictions.json`(회차, 생성일시, 조합 리스트)로 출력

4. **README 자동 갱신 로직 작성** → 검증: 마커 사이 텍스트가 `predictions.json` 내용과 일치하는지 스크립트 실행 후 diff 확인
   - `scripts/update_readme.py`: 마커 사이 블록을 최신 예측으로 치환
   - "참고용/오락 목적" 안내 문구 고정 포함

5. **GitHub Actions 워크플로우 작성** (`.github/workflows/lotto.yml`) → 검증: 로컬에서 `act` 또는 수동 `workflow_dispatch`로 1회 트리거해 성공 확인
   - `on: schedule: cron: '10 12 * * 6'`, `workflow_dispatch:`
   - Steps: checkout → setup-python → pip install → collect.py → predict.py → update_readme.py → git add/commit/push (변경 있을 때만)

6. **단위 테스트 작성** → 검증: `pytest` 전체 통과
   - `tests/test_collect.py`: 중복 회차 스킵, API 실패시 스킵 로직
   - `tests/test_predict.py`: 패턴 필터 함수 개별 검증 (홀짝/구간/연속/총합)

---

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| 비공식 API가 예고 없이 변경/차단될 수 있음 | `collect.py`에 응답 스키마 검증 + 실패 시 워크플로우가 실패하지 않고 경고 로그만 남기도록 처리 (Acceptance Criteria #6) |
| GitHub Actions 무료 티어 실행 시간/횟수 제한 | 주 1회 실행으로 최소화, 스크립트 실행시간 수 초 내외로 설계 |
| 예측이 실제로는 무작위와 통계적으로 다르지 않음 (기대치 오해) | README에 "통계적 예측 근거 없음, 오락 목적" 문구 고정 삽입 |
| 매주 자동 커밋으로 커밋 히스토리 오염 | 변경사항 없을 시 커밋 스킵 (`git diff --quiet` 체크) |

---

## Verification Steps

1. `pip install -r requirements.txt && pytest` — 전체 테스트 통과
2. `python scripts/collect.py` 로컬 실행 → `data/draws.json` 회차 증가 확인
3. `python scripts/predict.py` → `predictions.json`에 패턴 조건 만족하는 5세트 생성 확인
4. `python scripts/update_readme.py` → README 마커 블록 갱신 확인
5. GitHub 저장소 생성 후 Actions 탭에서 `workflow_dispatch` 수동 실행 → 성공 및 커밋 발생 확인
6. 다음 토요일 정기 스케줄 실행 후 README 자동 갱신 확인
