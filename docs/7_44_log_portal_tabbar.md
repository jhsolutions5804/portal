# 개발로그 — 포털: 하단 다중 작업탭 신설

> 작성: 춘식이(Claude) · 2026-09-23

## 요청

대표님 — 업무 보다 보면 이 메뉴 저 메뉴 다 봐야 하는데, 화면 하단에 탭이 생기게 해서 여러 메뉴를 오가며 업무 볼 수 있게 해달라. 탭은 최대 10개 정도.

## 구현

단일 `iframe#emb-frame`을 모듈별 iframe 여러 개(스택)로 바꾸고, 활성 탭만 보이도록 `display`를 토글하는 방식으로 `openModule` 전체 로직을 재작성. 같은 모듈 안의 서브탭 전환은 기존 `postMessage` 방식을 그대로 유지(새 탭을 만들지 않음). 상세 설계는 `0_5_portal_tabs.md` 참고.

- 최대 10개(`JH_TABS_MAX`), 초과 시 안내 후 차단.
- 하단 탭바(`#jh-tabbar`)는 `.main` 안쪽에 배치해 사이드바와 겹치지 않음.
- 탭 목록은 `sessionStorage`에 저장해 새로고침 후에도 같은 세션 안에서는 복원(단, 화면 전환은 강제하지 않고 iframe 내부 입력값까지는 복원 안 됨).

## 검증

- `node --check` 전체 스크립트 구문 검증.
- jsdom으로 탭 관리 함수만 추출해 37개 시나리오 검증: 권한 체크 유지, 새 탭 생성/기존 탭 재사용(재로딩 없음), 서브탭 postMessage 전환, 탭 전환 시 표시 토글, 탭 닫기(인접 탭 활성화·마지막 탭이면 홈으로), 10개 초과 차단, sessionStorage 저장/복원 — 전부 통과.
- production/portal-test 파일 diff가 Firebase 설정 외 동일함 확인 후 독립 적용.

## 배포

portal-test 확인 후 production 동시 배포(대표님 "전부 본섭으로 넘겨"). 포털 홈 20260923a.

## 백업

`backup/v6.1.0/index.html` (production) — portal-test는 `backup/20260923a/index.html`.

## 관련 문서

`0_5_portal_tabs.md`, `8_32_log_2026-09-23_session.md`.
