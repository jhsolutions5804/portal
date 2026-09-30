# 개발로그 — 견적 목록 견적상태 필터 추가 + 상세 복귀 시 필터 유지 (gihoek 5.8.0)

> 작성: 춘식이(Claude) · 2026-09-30 · 배포: portal-test (본섭 대기)

## 요청

대표님 — ① 견적 목록에서 필터를 "진행중"으로 걸었는데 종결 견적이 보임, ② 필터 건 상태에서 견적서 진입 후 종결·뒤로가기 등을 하면 필터가 전부 초기화되므로 바로 직전 화면으로 복귀해야 함.

## 원인

1. `진행상태` 셀렉트는 `projects[].status`(현장 상태) 필터. 견적 `status`(active/closed/void)와 무관 → 진행중 현장의 종결 견적이 통과. 목록의 현장 뱃지("진행중")와 견적 태그("종결")가 같은 말을 써서 혼동.
2. `renderEst()`가 진입 시 `estFilter*`·`estPage`를 항상 리셋. 상세의 `← 견적 목록`, 폼 취소/저장, 삭제가 모두 이 함수를 호출.

## 변경 (`gihoek/index.html`)

| 항목 | 내용 |
|------|------|
| 필터 | 견적상태(전체/진행중/종결/폐기) 신설, 기존은 현장상태로 명칭 분리 |
| 복귀 | `renderEst(keep)`, `estBack()`, `estBackRender()`, `estListScroll` 도입 |
| 뒤로가기 | `pushState/replaceState({estView:1})` + `popstate` |
| 삭제 | 프로젝트 진입 상태면 프로젝트 화면, 아니면 유지된 목록으로 복귀 |

## 검증

- module JS `node --check` OK, CSS 괄호 depth 0.
- jsdom 15개 항목 PASS(필터 결과, 페이지·스크롤 복원, 종결 후 재진입 시 history 누적 없음, 브라우저 뒤로가기, 프로젝트 진입 복귀, 신규 진입 초기화).
- portal-test 설정값(`portal-test-6e0ff`) 유지 확인, 본섭 설정값 혼입 없음.
- 실제 Firebase 연동 화면 확인은 대표님 확인 대기.

## 배포·백업

- portal-test `gihoek/index.html` build 20260930a · ver 5.8.0 (test 기준 5.7.4 위에 패치).
- 백업: `backup/v5.8.0/gihoek/index.html` (portal-test).
- 본섭 반영은 지시 전까지 대기. 본섭은 별도로 패치 적용 예정(파일 통복사 금지).

## 참고

- 본섭 gihoek는 5.7.3, test는 5.7.4(프로젝트 목록 정렬 강건화)로 서로 다름 → 본섭 반영 시 5.7.4 포함 여부 확인 필요.
