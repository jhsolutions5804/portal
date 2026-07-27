# 7.2b. 기획(gihoek) 개발로그 — 보안 (200줄 분할, 7_2_log_gihoek_r5.md에서 이어짐)

> 작성: 춘식이(Claude)

---

## 2026-07-27 — via=portal 우회 접근 버그 수정 (심각)

### 발단
- pjt_manday 접근검증 작업 중 서브 메뉴 전수 점검 → gihoek이 `?via=portal`일 때 **검증 없이 즉시 splash를 제거하고 앱 화면을 표시한 뒤, 견적/정산/거래처/지출 전체 컬렉션을 onSnapshot으로 구독**하고 있던 것을 발견. 직접 접근 경로엔 `status==='approved' && (admin || perms.plan)` 검증이 있었지만 via=portal 경로엔 전혀 없었음
- 즉, 로그인만 되어 있으면(승인 여부·기획 권한 여부 무관) 주소창에 `?via=portal`만 붙여 회사 재무 데이터(견적·정산·거래처·지출) 전체를 열람할 수 있는 상태였음

### 수정
- `onAuthStateChanged` 콜백을 하나로 통합 — via=portal 여부와 무관하게 항상 `portal_users/{uid}.status==='approved' && (admin===true || perms.plan===true)`를 확인한 뒤에만 화면 표시·데이터 구독 시작
- via=portal일 때는 검증 통과 후 splash 제거 + `portal-embed` 클래스 + onSnapshot 5종 등록(기존 로직 그대로), 직접 접근 시엔 `startApp()`(거래처 시드/이전 로직 포함) 호출 — 이 초기화 방식 차이만 유지
- 검증 실패 시 무조건 `showDenied()`

### 검증
- `node --check` 문법 통과

### 배포
- 대표님 지시로 portal-test 생략, production 직접 배포
- 커밋: `gihoek/index.html`
- 백업: `backup/v5.1.4/gihoek/index.html` (수정 전 원본)
