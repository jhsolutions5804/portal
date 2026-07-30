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

## 2026-07-30 — 정산서 구역(zone) 자동인식 오판정 버그 수정

### 발단
- 대표님이 정산서 미리보기에서 "복합4동 3F FIZ FCU 14대 설치", "복합3동 3F FIZ FCU 14대 설치" 두 항목이 모두 반입 0/39, 설치 0/39로 표시되는 것(원래 각 14대 기준이어야 함)을 발견, "왜 FIZ가 로드되는지" 질문

### 원인
- `zoneGuess(title)`가 `PROGRESS_PROFILES.p4ph2.zones` 배열을 순서대로 검사해 키워드 첫 매치(first-match)로 구역을 판정
- 배열 순서가 `fiz(3F FIZ) → xob → c3(복합3동) → c4(복합4동) → wob → mfr` 였는데, 문제의 두 견적 항목명에 건물명("복합3동"/"복합4동")과 설비타입("3F FIZ")이 함께 들어있어 항상 배열 앞쪽의 `fiz`(kw: '3F FIZ','FIZ')에 먼저 매치되어버림 → 실제 14대 항목이 39대 기준의 `fiz` 존으로 오배정

### 검토한 대안
- 키워드 길이가 긴 쪽 우선(longest-match) 방식도 시도했으나, "3F FIZ"(6자)가 "복합4동"(4자)보다 길어 여전히 오매칭됨 → 폐기

### 수정
- `zoneGuess` 로직은 원래의 first-match 그대로 유지
- `zones` 배열 순서를 건물명(복합3동·복합4동, 구체적)이 설비타입(3F FIZ 등, 포괄적)보다 **앞에 오도록** 재배치
- 배열에 주석 추가: 향후 zone 추가 시 순서 유의사항 명시

### 검증
- `node --check` 문법 통과
- 재현 케이스 3건("복합4동 3F FIZ...", "복합3동 3F FIZ...", "3F FIZ FCU 39대...") 노드 스크립트로 판정 결과 확인 → 각각 c4/c3/fiz로 정상 판정

### 배포
- 대표님 확인 후 production 직접 배포
- 커밋: `gihoek/index.html`, `index.html`(버전 배너, gihoek 5.3.1)
- 백업: `backup/v5.3.1/gihoek/index.html` (수정 전 원본)
- 문서: `docs/1_4_gihoek_settle.md` r3 갱신 (구역 자동인식 로직 + 주의사항 문서화)

### 후속 조치 필요
- 기존에 이미 `fiz`로 잘못 저장된 정산서가 있다면 대표님이 정산서 상세에서 구역 드롭다운으로 수동 재선택 필요 (자동 마이그레이션 없음)

