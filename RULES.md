# 예측 조건 (RULES.md)

이 문서는 `predict.py`가 실제로 읽어서 적용하는 예측 조건입니다.
조건을 바꾸려면 아래 설명과 `yaml` 코드블록을 함께 수정하세요 (코드블록만 파싱됩니다).

## 조건 설명

- 홀짝 비율: 홀수 개수 2~4개 (짝수는 나머지)
- 연속번호: 최대 2개까지만 허용 (예: 12,13은 허용, 12,13,14는 불허)
- 총합 범위: 6개 번호 합이 100~170 사이
- 구간별 개수:
  - 1-9번대: 0~3개
  - 10-19번대: 0~3개
  - 20-29번대: 0~3개
  - 30-39번대: 0~3개
  - **40-45번대: 반드시 1개 포함 (최소1, 최대1)**
- 예측 세트 수: 5세트

## 규칙 정의 (predict.py가 읽는 블록)

```yaml
frequency:
  all_time_weight: 0.4
  recent_weight: 0.6
  recent_window: 20

pattern_filters:
  odd_even_ratio: [2, 4]
  max_consecutive: 2
  sum_range: [100, 170]
  zones:
    - range: [1, 9]
      min: 0
      max: 3
    - range: [10, 19]
      min: 0
      max: 3
    - range: [20, 29]
      min: 0
      max: 3
    - range: [30, 39]
      min: 0
      max: 3
    - range: [40, 45]
      min: 1
      max: 1

num_predictions: 5
exclude_numbers: []
include_numbers: []
```
