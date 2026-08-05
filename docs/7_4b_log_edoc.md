# 7.4b. 개발로그 — 전자결재 (금액 콤마 포맷, 2026-07-23~)

> `7_4_log_edoc.md`가 200줄을 초과해 이어서 작성. 이전 이력은 `7_4_log_edoc.md` 참고.

---

## 2026-07-23 세션 — 금액 입력창 1000단위 콤마 포맷 적용

### 배경
대표님 지시: "포탈 내 모든 금액 입력·출력은 1000단위마다 콤마(,) 표시" (전 모듈 공통 UI 컨벤션)

### 변경 내용
`DOC_CONFIG`의 구매품의서 `unitPrice`, 지출결의서 `amount` 필드 타입을 기존 `'number'`에서 신설한 `'money'`로 변경:
- 렌더러(`renderDocForm` 내 필드 생성 분기)에 `f.type==='money'` 케이스 추가 — `type="text" inputmode="numeric"` + `oninput="fmtMoney(this)"`로 실시간 콤마 표시
- `docSave`에도 `f.type==='money'` 분기 추가 — 저장 시 콤마·비숫자 문자를 제거한 뒤 `Number()`로 변환해 저장(기존 `number` 타입은 `el.value`를 그대로 저장하던 구조라, 콤마가 섞이면 문자열로 잘못 저장될 위험이 있어 별도 파싱 필요했음)
- 상세보기(`docDetail`)도 `f.type==='money'`인 필드는 `Number(v).toLocaleString('ko-KR')+'원'` 형식으로 표시하도록 분기 추가
- 초과근로(overtime)의 수당(`amount`)/통상임금(`rate`)은 `DOC_CONFIG`상 `type:'number'`로 남아있으나, 실제 사용자 입력 폼(`renderOvertimeWrite`)은 이 설정을 쓰지 않고 근로자 등록 시급 기준 자동계산이라 사용자가 직접 타이핑하는 금액 입력창이 아님 — 콤마 포맷 대상에서 제외(현행 유지)

전역 헬퍼 `window.fmtMoney(el)` 신설(gihoek/hr과 동일 로직).

### 검증
- `node --check`로 모듈 스크립트(.mjs 추출) 문법 검증 통과

### 배포
- portal-test 선배포(기존 test 원본의 사소한 차이 — 초과근로 목록 `authorUid` 필터 미적용 상태 — 보존한 채로 개별 패치 적용) → 대표님 확인("오케이") → production 배포
- production: `edoc/index.html` 배포 완료, Pages 빌드 `built` 확인

### 문서
- `docs/3_3_edoc_docs.md` r2 갱신

---

## 2026-07-24 세션 — 구매품의서/지출결의서 품목 다중입력 + 개별 링크

### 요청
대표님 지시:
1. 지출결의서에 구매 링크 추가 (기존엔 구매품의서에만 참고링크 있었음)
2. 품의서·결의서 모두 구매 품목·수량을 여러 개 입력 가능하게
3. 품목/수량/단가를 폼 하단으로 이동, 가로 배치
4. 품목별로 개별 링크 추가 가능하게

### 변경 내용
`DOC_CONFIG`에 신규 필드 타입 `'items'` 도입 (품목명·수량·단가·링크를 한 행으로 묶어 다중 입력):
- **구매품의서(`purchase`)**: 기존 단일 `item`/`qty`/`unitPrice`/`refUrls`(다중 링크, 품목과 분리) 필드를 모두 제거하고 `items` 필드 하나로 통합. 필드 순서도 공급업체→목적→필요일→**품목(하단)**으로 재배치
- **지출결의서(`expense`)**: 기존 필드(지출일/구분/금액/거래처/목적/증빙)는 그대로 두고 `items` 필드를 하단에 신설 — 총 지출 금액(`amount`, 수기)은 유지하면서 품목별 상세·링크만 추가

구현:
- `renderDocWrite`: `f.type==='items'` 분기 추가 — 헤더 라벨(품목명/수량/단가/링크) + 행 컨테이너 + `+ 품목 추가` 버튼
- `window.addItemRow(key, values)` 신설 — 품목명(text)·수량(number)·단가(money, `fmtMoney` 실시간 콤마)·링크(url) 4칸 가로 배치 행 생성, `−` 버튼으로 개별 삭제
- `docSave`: `f.type==='items'` 분기 — `.item-row`를 순회해 `{name, qty, unitPrice, amount:qty×unitPrice, link}` 배열로 수집, 4값 모두 빈 행은 제외
- `window.fmtItemsTable(items)` 신설 — 상세보기/인쇄(A4)에서 품명·수량·단가·금액·링크 표 + 합계 행으로 렌더링. `docDetail`, `printDocA4` 양쪽에 적용
- `window.getItemsForDisplay(d, dtype)` 신설 — **하위호환**: `items` 도입 이전(레거시 `item`/`qty`/`unitPrice`/`refUrls` 구조)에 저장된 구매품의서를 조회할 때, 레거시 필드로 1행짜리 items를 구성해 동일한 표로 표시(읽기 전용 변환, 저장 구조는 건드리지 않음)

### 검증
- `node --check`로 모듈 스크립트 전체 문법 검증 통과
- jsdom으로 품목 행 추가/입력값 수집(수량×단가 자동계산)/빈 행 제외/삭제 동작 테스트 → PASS
- `fmtItemsTable` 렌더링(품목명·링크 표시, 합계 정확) 테스트 → PASS
- `getItemsForDisplay` 레거시 문서 하위호환(1행 변환) / 신규 구조 우선 사용 / 필드 없는 경우 빈 배열 테스트 → PASS

### 배포
- 테스트서버 원본(`portal-test`)이 production과 미세하게 다름(초과근로 목록 `authorUid` 필터 라인 부재) — 기존 차이 보존한 채 테섭 원본에 동일 패치 개별 적용 후 배포
- 대표님 확인("확인했어") → production 배포 승인
- production: `edoc/index.html` 배포 완료
- `index.html` 버전주석 갱신: build 20260724, `edoc 3.2r2` → `edoc 3.3`
- 백업: `backup/v2.6.4/edoc/index.html` (변경 전 원본)

### 문서
- `docs/3_3_edoc_docs.md` r3 갱신 (items 필드 구조, 하위호환 로직 반영)

---

## 2026-07-24 세션 (2) — 전자결재 홈 하단 패널 4개 클릭 시 전체목록 연결

### 요청
대표님(스크린샷 첨부): "전자결재 홈에서, 하단에 카드 4개 모두 상세 게시판으로 이동할 수 있게 하면 좋겠어. 지금 기능으로는 게시된 문건도 저기에 리스트 뜨는 것들만 확인할 수 있잖아."

### 조사
`renderEdocHome()` 구조 확인 결과:
- 상단 KPI 카드 4개(결재 요청/수신함/내 문서/게시 문건)는 이미 `onclick="edocShowList(kind)"`로 전체 목록 모달 연결돼 있었음
- 그러나 그 아래 패널 4개(내가 결재해야 할 문서/수신함(회람)/내가 작성한 문서/게시된 문건)는 `.slice(0,8)` 미리보기만 렌더링하고 클릭 이벤트가 없어, 대표님이 실제로 언급한 "하단 카드"(패널)에서는 전체 목록에 접근할 방법이 없었음

### 변경 내용
`edoc/index.html` `renderEdocHome()`의 패널 4개 헤더(`.panel-head`)에:
- `onclick="edocShowList(kind)"` 추가 (kind: `approve`/`inbox`/`mydocs`/`posted`, KPI 카드와 동일 매핑)
- 우측에 "전체보기 ›" 텍스트 추가해 클릭 가능함을 시각적으로 표시
- 새 페이지/게시판을 만들지 않고 기존 `edocShowList` 모달(전체 건수, 상태·작성자·날짜 표시, 클릭 시 상세 이동)을 재사용

### 검증
- `node --check` 문법 검증 통과
- 4개 패널의 onclick kind 값이 `edocShowList`의 `TITLES`/`EMPTY` 매핑 키와 정확히 일치하는지 코드 대조 확인

### 배포
- portal-test 개별 패치 적용(테섭↔prod 기존 차이 보존) → 대표님 확인("뜨긴 한다") → production 배포 승인("이거 본섭에 반영해줘")
- production: `edoc/index.html` 배포 완료
- **버전주석 이슈 발견**: 배포 시점에 `index.html` 버전주석이 동일 날짜(20260724)에 다른 세션의 PJT 5.0.0 대규모 업데이트로 덮어써져 있었고, 그 세션이 오래된 사본을 베이스로 작업했는지 `edoc 3.3`(이번 세션 오전 갱신분)·`hr 2.6.3`·`gihoek 1.4r2` 표기가 `edoc 3.2r1`·`hr 2.6.2`로 되돌아가 있었음(실제 코드 파일은 손상되지 않음, `gihoek/index.html`·`hr/index.html`의 `fmtMoney`/`numClean` 존재 확인으로 검증). PJT 5.0.0 변경 내역은 보존한 채 모듈 버전 표기만 정정하고 이번 패널 클릭 기능 항목을 추가해 병합

### 문서
- `docs/3_0_edoc_home_approve.md` r2 갱신 (홈 대시보드 구조, `edocShowList` 연결점 문서화 — 기존 문서가 2026-07-06 이후 갱신 안 돼 있어 현행화 겸함)

---

## 2026-07-27 — via=portal 우회 접근 버그 수정

### 발단
- 대표님 지시로 pjt_manday에 페이지 자체 접근 검증을 추가하던 중, 다른 서브 메뉴들도 전수 점검 → edoc에 로그인 검증 로직 자체는 있지만 `?via=portal` 파라미터가 있으면 승인·권한(`perms.edoc`) 여부와 무관하게 무조건 `enterApp()`으로 입장시키는 우회 버그 발견

### 수정
- `onAuthStateChanged` 콜백을 하나로 통합 — via=portal 여부와 무관하게 항상 `portal_users/{uid}.status==='approved' && (admin || perms.edoc)`를 확인한 뒤에만 입장 허용
- via=portal일 때는 검증 통과 후 `portal-embed` 클래스만 추가로 적용(포털 임베드 스타일용) — 그 외 검증 로직은 직접 접근과 완전히 동일
- 검증 실패 시 무조건 `show('denied')`

### 검증
- `node --check` 문법 통과

### 배포
- 대표님 지시로 portal-test 생략, production 직접 배포
- 커밋: `edoc/index.html`
- 백업: `backup/v5.1.4/edoc/index.html` (수정 전 원본)


## 2026-08-05 — fetchEdocDocs 함수 스코프 버그 수정

### 발단
- 대표님 스크린샷 제보: 연차신청서, 지출결의서 화면에서 `오류: fetchEdocDocs is not defined` 표시, 페이지 로드 안 됨

### 조사
- `edoc/index.html` 전수 검색 결과 `fetchEdocDocs`는 `renderEdocHome()` 함수(862~1062줄) 내부에 중첩 선언(915줄)되어 있었음
- 전자결재 홈 자체는 같은 함수 스코프 내 호출이라 정상, 하지만 별도 최상위 함수인 `renderDocList()`(1789줄, 연차·구매품의·지출결의 등 목록 공용 렌더러)와 `loadApproveData()`(1106줄, 결재함)는 스코프 밖이라 `ReferenceError` 발생

### 수정
- `fetchEdocDocs()` 함수 선언을 `renderEdocHome()` 밖, 모듈 최상위로 이동
- 함수 내부 로직은 전혀 변경하지 않음(순수 스코프 이동)

### 검증
- `node --check`로 module script 구문 검증 통과
- 원본과 diff 비교 → 함수 블록 위치 이동 외 변경 없음 확인
- 중복 선언 없음(grep으로 단일 정의 확인)

### 배포
- 대표님 지시로 portal-test 생략, production 직접 배포
- 커밋: `edoc/index.html`
- 백업: `backup/v5.3.6/edoc/index.html` (수정 전 원본)
- `index.html` 버전주석: edoc 3.4r2 → 3.4r3

