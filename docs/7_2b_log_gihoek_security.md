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

## 2026-07-30 (2) — 정산서 공급가액/부가세 수동수정 + 공수연동 자동집계 오차 수정

### 요청
1. 정산서 발행 화면에서 공급가액·부가세를 직접 수정할 수 있게 해달라
2. SUP(ph4) 7월 실투입 공수가 8.0인데 정산서 공수연동은 19.6으로 집계됨. FAB도 pjt_manday(309.0)와 정산서 자동집계(315) 불일치

### 진단
- (1)은 신규 기능 요청 — 기존엔 `renderSetTot()`가 자동계산값만 읽기전용 표시
- (2) 원인: `fetchManday()`가 `worker_manday`/`ph4_manday` 일별 문서의 `md` 값을 **명부 검증 없이 전부 합산**. 반면 `pjt_manday`(월간 공수 집계) 화면은 합산 전 해당 ID가 `pjt_workers_fab`/`pjt_workers_ph4`(현재 유효 명부)에 있는지 검증하고, 없으면 무시함(`unknownIdCount`로만 집계). 근로자 마스터 정리·중복 통합 과정에서 남은 구 ID 잔재 데이터가 정산서 쪽에서만 그대로 합산되어 두 화면 수치가 어긋난 것

### 수정
1. `settleDraft`에 `supplyOverride`/`vatOverride` 필드 추가. `renderSetTot()`의 공급가액·부가세를 `<input>`으로 변경, `onchange`로 오버라이드 저장(`setSupplyOverride`/`setVatOverride`). `effSupply()`/`effVat()` 헬퍼로 오버라이드 우선 적용, 없으면 기존 자동계산. 오버라이드 상태일 때 자동계산값 병기 + "자동계산으로 되돌리기" 링크(`resetSetTot`). `publishSettle()`도 `effSupply()`/`effVat()` 사용하도록 변경
2. `fetchManday()`에 명부 필터링 추가: 프로젝트 종류(FAB/SUP)에 따라 `pjt_workers_fab`/`pjt_workers_ph4`를 조회해 ID셋 구성 → 그 안의 ID만 합산, 명부 외 공수는 제외하고 토스트로 제외량 안내

### 검증
- `node --check` 문법 통과 (import 구문 제거 후 `.mjs` 재검증)
- 원격 최신본과 diff 확인 후 배포(직전 zone 버그 수정 건과 충돌 없음 확인)

### 배포
- 커밋: `gihoek/index.html`, `index.html`(버전배너, gihoek 5.3.2)
- 백업: `backup/v5.3.2/gihoek/index.html`
- 문서: `docs/1_4_gihoek_settle.md` r4 갱신

## 2026-07-30 (3) — 정산서-견적 연결 기능 추가 (기청구 미반영 문제)

### 발단
- 대표님이 "FAB동 3F FIZ FCU 39대 설치" 견적으로 공정 정산서를 작성했는데 "기청구"가 0으로 뜨는 것을 지적. 7/3에 이미 같은 설비(FCU 34대, 73,850,000원)로 "직접입력" 방식 청구서를 발행한 상태였음

### 원인
- `priorByEst(estId)`는 `settlements`에서 `docType==='invoice' && s.perEst[estId]`가 있는 것만 합산
- `perEst`는 발행 시 `method==='progress'`/`'qty'`일 때만 자동 채워짐. `method==='manual'`(직접입력)은 `perEst`가 비어있는 채로 저장되어, 같은 물리적 설비라도 견적과 연결이 안 됨 → 기청구 0

### 수정
- 정산서 상세화면에 "🔗 견적 연결" 버튼 추가 (`docType==='invoice'` && `method` in `manual`/`qty`)
- `linkSettleToEst(id)`: 프로젝트 내 견적 목록에서 선택 → 반영 금액 입력 → `perEst` merge 저장
- 연결 상태는 상세화면에 안내 배너로 표시, 재연결(수정) 가능

### 검증
- `node --check` 문법 통과, 원격 최신본과 diff로 신규 추가분만 있음을 확인 후 배포

### 배포
- 커밋: `gihoek/index.html`, `index.html`(버전배너, gihoek 5.3.3)
- 백업: `backup/v5.3.3/gihoek/index.html`
- 문서: `docs/1_4_gihoek_settle.md` r5

### 후속조치 필요
- 대표님이 7/3 청구서(73,850,000원)를 "FAB동 3F FIZ" 견적에 수동으로 연결해야 함 (자동 소급 매칭 없음)

## 2026-07-30 (4) — 정산서-견적 연결을 항목별 개별 지정으로 개선

### 요청
- r5의 "견적 연결"이 정산서 1건당 견적 1곳만 연결 가능했는데, 실제로는 한 청구서에 FIZ/X-OB/복합3동/복합4동/관리자파견 등 여러 항목이 섞여있어 항목별로 각각 다른 견적에 연결하고 싶다는 요청

### 수정
- `linkSettleToEst`를 prompt 2회 방식에서 모달 UI로 전면 교체: `s.lines`(청구서 내역) 각각에 견적 선택 드롭다운 표시
- `saveLinkEst`: 항목별 선택값을 `perEstLines`(라인idx→견적ID, 재편집용)로 저장하고, 같은 견적으로 연결된 라인들의 금액을 합산해 `perEst`(견적ID→합산금액)로 저장 — `priorByEst()`는 수정 없이 그대로 호환
- 모달은 기존 `plan-list-modal`과 동일한 구조/스타일 패턴 재사용

### 검증
- `node --check` 통과, 원격 최신본과 diff로 의도한 변경분만 확인 후 배포

### 배포
- 커밋: `gihoek/index.html`, `index.html`(버전배너, gihoek 5.3.4)
- 백업: `backup/v5.3.4/gihoek/index.html`
- 문서: `docs/1_4_gihoek_settle.md` r6

## 2026-07-30 (5) — 정산 목록 필터(구분/PJT/거래처/상태) 추가

### 요청
- 대금청구서/지급예정서 구분, PJT별, 거래처별 필터링 요청 → 이어서 완결/미결 상태 필터도 추가 요청

### 수정
- `renderSettle()`에 필터 바 추가: 구분(`docType`)/PJT(`pjtId`)/거래처(`recipient.company`, 동적 목록)/상태(`done`/`pending`)
- `window.settleFilter`(세션 메모리)에 현재 필터 저장, `setSettleFilter(key,val)`/`resetSettleFilter()`로 갱신 시 재렌더
- 상단 요약(청구누계/지급예정누계/미수금)도 필터된 배열 기준으로 재계산되도록 변경

### 검증
- `node --check` 통과, 원격 diff로 의도한 변경분만 확인 후 배포

### 배포
- 커밋: `gihoek/index.html`, `index.html`(버전배너, gihoek 5.3.5)
- 백업: `backup/v5.3.5/gihoek/index.html`
- 문서: `docs/1_4_gihoek_settle.md` r7

