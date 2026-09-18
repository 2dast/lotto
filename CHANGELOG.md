# Changelog

## [1.1.0](https://github.com/2dast/lotto/compare/v1.0.0...v1.1.0) (2026-09-18)


### Features

* add release-please for conventional-commit-driven semver ([9aa62cd](https://github.com/2dast/lotto/commit/9aa62cdc7b40c5c04b66e73caf35743e6006a81a))
* add responsive off-canvas sidebar for mobile/web support ([2fbc701](https://github.com/2dast/lotto/commit/2fbc701bcd7126d7afcb09e7ef8cfde09cb34de3))
* **astro-app:** astro 스캐폴딩 + 예측엔진/수집 로직 TS 포팅 ([3d336b4](https://github.com/2dast/lotto/commit/3d336b402f7c8bd297d1ec7a8abbaad631e15279))
* **astro-app:** predictions Content Layer 컬렉션 배선 ([9d84dcc](https://github.com/2dast/lotto/commit/9d84dccc2e8fceb0c5f9e4f2e1a924e5f1308112))
* **astro-app:** 가중 랜덤 추출·조합 생성 로직 TS 이식 (T4) ([cc1141f](https://github.com/2dast/lotto/commit/cc1141f8ad9ddb3adc753327891a8bf4ea474d5f))
* **astro-app:** 대시보드 페이지 Astro 이식 (T8) ([d6d9e61](https://github.com/2dast/lotto/commit/d6d9e6188764bd1c3f058bcfc8c32cd739fea2e1))
* **astro-app:** 리포트 목록 페이지 + 예측표/차트 컴포넌트 이식 (T9,T10) ([3ba9f5a](https://github.com/2dast/lotto/commit/3ba9f5ac149fa9f3561b97169608b96cd4ef9f4a))
* **astro-app:** 리포트 상세 페이지 조립 (T11) ([119b602](https://github.com/2dast/lotto/commit/119b6023439803bccda59dd244198658db2053ca))
* **astro-app:** 번호 점수화 + Content Layer draws 컬렉션 이식 (T2,T6) ([7ccae0f](https://github.com/2dast/lotto/commit/7ccae0ffd59b2a74355bda0cfdab64b75373cd98))
* **astro-app:** 예측 생성/최신 조회 loader TS 이식 (T7) ([1a6e2cf](https://github.com/2dast/lotto/commit/1a6e2cf8bb6e85a341d2f73c1efd6e7797098a75))
* compute prediction hits client-side, remove accuracy tracking pipeline ([baf7f82](https://github.com/2dast/lotto/commit/baf7f8207dc2b72acfa978f002ad751679008335))
* organize predictions and reports into per-round directories ([902df21](https://github.com/2dast/lotto/commit/902df21310767f928f20b0c8179d37f869cf38ff))
* **report:** apply design.md token system to report index sidebar ([90b787f](https://github.com/2dast/lotto/commit/90b787f245b219eb2ef94d459d4e3efb4244a532))
* **report:** label the strip chart y-axis, drop redundant coverage chart ([35f61db](https://github.com/2dast/lotto/commit/35f61db2dfe751d4fbca9ab322f770147ab9166e))
* **report:** redesign screening report for readability and consistency ([9a5bbce](https://github.com/2dast/lotto/commit/9a5bbcec7716b7ae8bc70e995c0bba31b37c54fa))
* **report:** restructure around explaining this round's recommendation ([a8d9903](https://github.com/2dast/lotto/commit/a8d9903933e0bd5fa1305522d0b527cf33c30814))


### Bug Fixes

* **astro-app:** GitHub Pages 프로젝트 사이트 base path 설정 ([ffd3b2c](https://github.com/2dast/lotto/commit/ffd3b2c77f6068475743bc89d3e9941f01575de1))
* **ci:** package-lock.json을 npm ci와 동기화 ([52bb142](https://github.com/2dast/lotto/commit/52bb142ac5631bcdea128313c56698ffb965d5c7))
* **dashboard:** 클라이언트 JS로 삽입되는 예측 번호 공 스타일 미적용 수정 ([69499f3](https://github.com/2dast/lotto/commit/69499f3468f00ad1a6c3d54c44a1d1ed74dcd14f))
* 모바일 대시보드 가로스크롤 및 터치 타겟 개선 ([3ee574d](https://github.com/2dast/lotto/commit/3ee574d97ae6bd5bad0880d8a5b8b1d4733a4e5e))


### Reverts

* don't force-expand the first sidebar round group ([fda6222](https://github.com/2dast/lotto/commit/fda6222cacf083de81dad06a5030c20495f7fbff))
