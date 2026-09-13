# 커밋 메시지 규칙

이 저장소는 [release-please](https://github.com/googleapis/release-please)로 버전(semver)과
`CHANGELOG.md`를 자동 관리합니다. main에 머지되는 커밋 메시지가 아래 [Conventional Commits](https://www.conventionalcommits.org/)
형식을 따라야 자동 버전 계산이 정확히 동작합니다.

## 형식

```
<type>[(scope)]: <설명>

[본문]

[BREAKING CHANGE: <설명>]
```

## 버전에 영향을 주는 type

| type | 버전 영향 | 예시 |
|---|---|---|
| `fix` | patch (1.0.x) | `fix: correct KST timezone offset in report timestamps` |
| `feat` | minor (1.x.0) | `feat: add number-distribution and overlap charts to report` |
| `feat!` 또는 본문에 `BREAKING CHANGE:` | major (2.0.0) | `feat!: replace reports/index.html with unified dashboard at root` |

## 버전에 영향을 주지 않는 type

`chore`, `docs`, `refactor`, `test`, `style`, `ci` — CHANGELOG에도 기본적으로 노출되지 않음.

```
chore: update lotto data and predictions
docs: update README with report screenshot
refactor: simplify generate_report.py data computation
```

## 동작 방식

1. main에 push될 때마다 `release-please` 워크플로우가 마지막 릴리스 이후 커밋들을 스캔한다.
2. `fix`/`feat`/`feat!` 중 가장 높은 등급에 맞춰 다음 버전을 계산하고, 버전 올림 + `CHANGELOG.md` 갱신을 담은 **Release PR**을 자동으로 만들거나 갱신한다.
3. 그 Release PR을 **사람이 확인 후 머지**하면, 그 순간 git tag(`vX.Y.Z`)와 GitHub Release가 자동 생성된다.

즉 커밋 메시지 type 선택과 Release PR 머지 승인만 사람이 하고, 버전 계산·태깅·CHANGELOG 작성은 전부 자동이다.
