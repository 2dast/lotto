# 예측 조건

한 줄에 조건 하나씩 적습니다. `#`으로 시작하면 주석(무시)입니다.
조건을 추가/삭제/수정할 때는 이 줄들만 건드리면 됩니다 — `predict.py`가 매번 새로 읽어서 해석합니다.

```
odd_even 1 5               # 홀수 개수 1~5개 허용 (실제 1240회차 5~95pct 기준)
sum 88 189                 # 6개 번호 합계 88~189 (실제 5~95pct 기준)
consecutive_max 3          # 연속번호 최대 3개까지 (실제 95pct 기준)
zone 1 9 min 0 max 3       # 1~9번대는 0~3개
zone 10 19 min 0 max 3     # 10~19번대는 0~3개
zone 20 29 min 0 max 3     # 20~29번대는 0~3개
zone 30 39 min 0 max 3     # 30~39번대는 0~3개
zone 40 45 min 0 max 2     # 40~45번대는 0~2개 (실제 평균 0.8개, 5~95pct 기준)
predictions 5              # 예측 세트 5개 생성
freq_all_weight 0.4        # 전체 출현 빈도 반영 비중 40% (백테스트 결과 실제 확률과 무관, 취향 반영용)
freq_recent_weight 0.6     # 최근 회차 출현 빈도 반영 비중 60% (백테스트 결과 실제 확률과 무관, 취향 반영용)
freq_recent_window 20      # "최근"의 기준 = 최근 20회차
```

## 조건 종류 설명

| 키워드 | 형식 | 의미 |
|---|---|---|
| `odd_even` | `odd_even <최소> <최대>` | 홀수 개수 허용 범위 (예: `2 4` = 홀수 2~4개) |
| `sum` | `sum <최소> <최대>` | 6개 번호 합계 허용 범위 |
| `consecutive_max` | `consecutive_max <n>` | 연속번호 최대 허용 개수 |
| `zone` | `zone <시작> <끝> min <최소개수> max <최대개수>` | 특정 구간에서 뽑을 개수 강제 (min=max면 정확히 그 개수) |
| `predictions` | `predictions <n>` | 생성할 예측 세트 수 |
| `freq_all_weight` | `freq_all_weight <0~1>` | 전체 출현 빈도 가중치 |
| `freq_recent_weight` | `freq_recent_weight <0~1>` | 최근 출현 빈도 가중치 |
| `freq_recent_window` | `freq_recent_window <n>` | "최근"으로 볼 회차 수 |
| `exclude` | `exclude <번호> [번호...]` | 예측에서 항상 제외할 번호 |
| `include` | `include <번호> [번호...]` | 예측에 항상 포함할 번호 |

### 예시: 조건 추가/수정
- "40번대는 반드시 1개" → `zone 40 45 min 1 max 1` 로 수정
- "1번대(1-9)는 아예 뽑지 말자" → `zone 1 9 min 0 max 0` 으로 수정
- "7번은 항상 포함" → `include 7` 줄 추가
