# 7.4. 개발 로그 — 전자결재 앱

> `portal/edoc/index.html` 변경 이력
> 최초 작성: 2026-06-26 · 작성: 춘식이(Claude)

---

## 커밋 이력

| SHA | 날짜 | 내용 |
|-----|------|------|
| *(Rev1)* | 2026-06-24 | 7개 탭: 홈·업무일지·연차·퇴직·재직·구매·지출 |
| *(Rev2)* | 2026-06-25 | 결재함 탭, 결재흐름 완성, 연차현황, A4출력, 고정결재라인, 제목자동, KPI모달 |
| `fde49ef998` | 2026-06-26 | Firebase config 원본 복원 |
| `0ff3cfaed0` | 2026-06-26 | 홈 KPI B안 팝업 통일 |
| *(미배포)* | 2026-06-26 | C1 직접 접근 인증 portal_users 통일 |

---

## Rev 1 → Rev 2 주요 변경 (2026-06-25)

| 항목 | 내용 |
|------|------|
| 결재함 탭 | 내 차례 문서 모아보기 |
| 결재 흐름 완성 | 상신→결재→승인/반려/게시, 회수, 권한 판정 |
| 고정 결재라인 | `buildFixedApprovalLine` — 퇴직원서: 김종화→김영희→송지훈+회람 김민서 |
| A4 출력/PDF | `printDocA4` — 전 문서 공통 |
| 문서 제목 자동 생성 | `yyyymmdd 이름 문서명` |
| 연차 현황 박스 | 로그인 계정의 부여/사용/잔여 카드 |
| KPI 카드 모달 | `edocShowList` — 목록 팝업 |

---

## Rev 2 이후 변경 (2026-06-26)

### Firebase config 복원
- `messagingSenderId: '36946317914'` (hr과 동일 이슈)

### KPI 팝업 B안 통일
- 4개 KPI 카드 모두 B안 디자인으로 통일
- B안: 상태 배지(배경색) + 제목/작성자 2줄 + 날짜 + 화살표(›)

### 직접 접근 인증 통일 (C1)
- 기존: 직접 URL 접근 시 구버전 `edoc_users/{uid}` 컬렉션 참조
- 변경: `portal_users/{uid}` 기반으로 통일
- 구버전 컬렉션 `edoc_users`, `edoc_requests` 참조 제거
- 직접 접근 시에도 `_isAdmin`, `_myInfo` 정상 세팅

---

## 이슈 & 해결

| 이슈 | 해결 |
|------|------|
| Rev1에서 일반 문서 결재 불가 | `docSave`에서 `buildFixedApprovalLine` 호출 추가 |
| `renderDocMain` window 미등록 → 뒤로가기 먹통 | `window.renderDocMain = renderDocMain` 추가 |
| 백틱 이중 이스케이프 SyntaxError | 바이트 치환: `content.replace(b'\\`', b'`')` |
| `<\/script>` A4 출력 조기 종료 | 이스케이프 필수 처리 |
| 직접 URL 접근 시 edoc_users 미존재로 접근 불가 | portal_users 기반으로 인증 통일 |

---

## 알려진 주의사항

- **module scope**: 모든 인라인 onclick 함수 `window.fn = fn` 등록 필수
- **show 함수 호이스팅**: `onAuthStateChanged`보다 앞에 정의
- 배포 전 `node --check`로 JS 문법 검증 필수

---

## PC 레이아웃·결재함·권한·네비게이션 개편 (N2~N9, 2026-06-30~07-01)

> Test server(`portal-test`)에서 무결점 테스트 후 main 이식 완료

### 커밋 이력 (main)
| SHA | 내용 |
|-----|------|
| `3a5ad393` | N2~N9 일괄 이식 (test 검증본) |

### 변경 항목
| 코드 | 내용 |
|------|------|
| N2/N4 | 포털 임베드(`portal-embed`) 시 파란 헤더·탭바 숨김 + PC(900px+) 콘텐츠 `max-width:1180px` 중앙정렬 |
| N5 | 결재함 `결재대기`/`결재완료` 서브탭 분리. `switchApproveSubTab`, `loadApproveData`(`_approvePending`/`_approveDone` 캐시), `renderApproveListUI`. 완결 판단: status가 approved/rejected/posted |
| N6-1 | 업무일지 열람 권한관리(관리자 전용). 데이터모델 `portal_users/{uid}.dailyViewTargets:[열람허용대상uid...]` = "X의 글을 Y가 볼 수 있다". 필터: 내 uid가 타인의 dailyViewTargets에 포함되면 그 사람 글 열람 가능. `renderDailyPerms`, `toggleDailyViewTarget`(칩 클릭 즉시 저장) |
| N6-2 | 업무일지 PC 테이블 레이아웃(`.ptable`/`.sec-toolbar`). 진입 시 바로 조회 테이블, 우측 상단 작성/권한관리 버튼 |
| N6-3~6 | 연차·퇴직원서·재직증명서·구매품의서·지출결의서 5개 탭 동일 테이블 레이아웃. `renderDocMain`→`renderDocList` 통합, `renderDocList` 1곳 수정으로 5탭 동시 적용. 연차는 작성함수 `renderLeaveWrite` 분기 |
| N7 | 각 탭에 "🏠 전자결재 홈" 버튼. 공통헬퍼 `edocHomeBtnHtml()`. portal-embed 시 헤더·사이드바 숨겨지므로 콘텐츠 툴바에 배치 |
| N8/N9 | 결재함 내용확인 → 뒤로가기 직전화면(결재함) 복귀. 전역 `_detailBackFn`(향후 `_navStack` 배열 확장 컨셉 주석 기록). `openDocFromHome`에서 설정, `docDetailBack`(실행 후 즉시 null 초기화). daily는 `DOC_CONFIG` 미정의 → `renderDailyDetail` 분기로 cfg undefined 버그 동시 수정 |

### 이슈 & 해결
| 이슈 | 해결 |
|------|------|
| N6-1 권한 방향 반대 구현 | "내가 부여한 대상"이 아닌 "내 글을 볼 수 있는 대상"으로 필터 방향 수정 |
| 퇴직원서~지출결의 "불러오는 중" 멈춤 | iframe 캐시 문제 (코드 정상). 강력 새로고침으로 해결 → 근본해결은 N11 |
| 목록 화면 "불러오는 중" 깜빡임 | 초기 로딩 문구 제거(빈 컨테이너), 데이터 오면 결과로 채움 |
| 결재함→업무일지 클릭 시 cfg undefined | daily는 renderDailyDetail로 분기 (N8/9와 동시 수정) |

---

## 2026-07-01 세션 — 구매품의서 참고링크 다중입력

> 버전: 전자결재 문서 **3.3.x → MINOR +1** (기능 추가)

### 변경 내용

| 코드 | 내용 |
|------|------|
| E1 | `DOC_CONFIG.purchase`에 `refUrls`(type='urls', 선택) 필드 추가 |
| E1 | `+ 링크 추가` 버튼으로 URL 무제한 입력, `−` 버튼으로 행 삭제 (`addUrlRow`) |
| E1 | 저장 시 URL 배열로 수집 (`.url-input` 클래스, 빈 값 제외) |
| E1 | 출력 포맷 `fmtDocVal` — URL 배열이면 전체 주소 대신 "링크"/"링크1·링크2" 하이퍼링크(새 탭)로 표시 |

### Main 이식
- `edoc/index.html` 커밋 `af5384ea6f` — test 전용 요소 없어 그대로 이식

---

## 2026-07-20 세션 — 업무일지 임시저장/반려 상태 수정 기능 추가

> 문서 버전: 3.1 → **r1**

### 배경 (원인 분석)
- 업무일지 상세화면(`renderDailyDetail`)에는 애초에 "수정" 버튼 자체가 없었음
- 작성화면(`renderDailyWrite`)도 항상 신규 등록(`addDoc`)만 지원 → 회수 후 임시저장 상태가 되어도 수정할 방법이 없었음
- 참고로 일반 문서 상세(`renderDocDetail`, leave 외 타입)도 수정 버튼을 누르면 "삭제 후 재작성해 주세요" 안내만 뜨는 구조 — 업무일지는 이번 건에서 leave처럼 실제 인라인 수정을 지원하도록 별도 구현

### 변경 내용
| 코드 | 내용 |
|------|------|
| `renderDailyDetail` | 기존에 계산만 되고 미사용이던 `canEdit`(작성자+draft/rejected)을 이용해 "✏️ 수정" 버튼 추가 |
| `renderDailyWrite(existingDoc)` | 인자로 기존 문서를 받으면 제목·일자·프로젝트·작성자정보·업무내용을 모두 미리 채우는 수정모드로 동작. 헤더에 "임시저장 상태 수정 중" 배지, 뒤로가기 시 상세화면 복귀. 인자 없이 호출(기존 "작성" 버튼)하면 기존과 동일하게 신규 작성 모드 |
| `dailySave(status)` | `window._dailyEditId` 설정 여부로 신규(`addDoc`)/수정(`setDoc merge`) 분기. 수정 시 `createdAt` 보존, `updatedAt`만 추가 기록. 저장 후 `_dailyEditId` 초기화 |

### 검증
- `node --check` (import 구문 제거 후) 전체 스크립트 문법 통과
- 기존 "작성" 버튼 호출부(`renderDailyWrite()` 무인자)와 하위호환 확인
- 특수문자(따옴표) 포함 데이터의 onclick 속성 이스케이프 정상 동작 확인 (기존 `printDocA4`와 동일 패턴 재사용)
- portal-test 우선 배포 → 대표님 실사용 확인("ㅇㅋ") → production 배포

### 운영 커밋
- `edoc/index.html` `86e4caaf` (test: `8a879856`)
- `index.html` (버전주석) — 동일 세션 내 갱신
- 백업: `backup/v2.6.0/edoc/index.html`

---

## 2026-07-21 세션 — 초과근로 상신 사유(reason) 필드 추가

> 문서 버전: 3.4 → **r2**

### 배경
- 대표님 요청: "초과근로 상신 시 사유 작성할 수 있게"
- 최초 시도로 `hr/index.html`(인사 앱의 관리자 직접입력용 초과근로 탭)을 먼저 수정했으나, 실제 요청은 **전자결재의 초과근로 상신 화면**(`renderOvertimeWrite`, 결재라인 있는 "상신" 폼)이었음 — 스크린샷으로 확인 후 정정
- 두 화면 모두 최종적으로 사유 필드를 추가함 (인사 직접입력분·전자결재 상신분 모두 지원)

### 변경 내용 — `edoc/index.html`
| 코드 | 내용 |
|------|------|
| `DOC_CONFIG.overtime.fields` | `{ key:'reason', label:'사유', type:'text' }` 추가 → `docDetail` 상세보기에 자동 표시 |
| `renderOvertimeWrite()` | "초과근로 정보" 카드에 `fcField('사유', <textarea id="ot-reason">)` 추가 (선택 입력) |
| `overtimeSave()` | `reason` 값을 읽어 trim 후 `edoc_overtime` 문서에 저장 |
| `docApprove()` (승인 시 인사 연동 블록) | `overtime` 컬렉션에 addDoc 할 때 `reason: rawData.reason||''` 포함 |

### 변경 내용 — `hr/index.html` (선행 작업, 함께 배포)
- 초과근로 탭 PC/모바일 입력폼·수정폼에 사유(선택) 텍스트영역 추가
- PC 상세 테이블 / 모바일 직원별 조회 / 전체현황 날짜별 상세 테이블에 사유 컬럼 추가 (긴 텍스트는 말줄임 + 툴팁)
- `otEsc()` 헬퍼 추가 (사유 등 자유 입력 텍스트 HTML 이스케이프)

### 설계 판단
- 사유는 **선택 입력**(필수 아님)으로 처리 — 기존 빠른 입력 흐름을 막지 않기 위함
- 기존 `overtime`/`edoc_overtime` 문서에는 `reason` 필드가 없으나, 화면에서 값이 없으면 "-"로 표시되므로 별도 마이그레이션 불필요

### 검증
- `node --check`로 각 파일의 비-module 스크립트(hr) / module 스크립트(edoc, `.mjs`로 추출) 문법 검증 통과
- portal-test 우선 배포 → 대표님 실사용 확인("확인됐어") → production 배포

### 운영 커밋
- portal-test: `hr/index.html` `b22d444`, `edoc/index.html` `859877f`
- production: `hr/index.html` `bc130cd`, `edoc/index.html` `820f134`, `index.html`(버전주석) `5ed6897`
- 백업: `backup/v2.6.1/hr/index.html`, `backup/v2.6.1/edoc/index.html`

---

## 2026-07-23 세션 — 초과근로 결재 목록 "본인 작성분만 표시" 필터 추가

### 배경
대표님 스크린샷 확인 결과, "초과근로 결재" 탭(`renderOvertimeMain`)에 결재자 본인이 상신하지 않은 **다른 직원의 상신 건**(이한영, 정다애 등)까지 전부 노출되고 있었음. 요청: "내 것 말고 다른 사람 것 안 보이게 해줘"

### 원인
`renderOvertimeMain()`이 `edoc_overtime` 컬렉션 전체를 필터 없이 조회 → 전 직원의 상신 건이 모두에게 노출됨. (다른 문서함(`renderDocList`)은 admin/posted/authorUid/approvalLine 기준의 `canView` 필터가 있었지만, 초과근로 전용 목록에는 애초에 필터 로직이 없었음)

### 수정
```js
const myUid=(_user&&_user.uid)||'';
docs=docs.filter(d=>d.authorUid===myUid);
```
- `renderOvertimeMain()`에서 조회 직후 `authorUid`가 현재 로그인 uid와 일치하는 문서만 남기도록 필터 추가
- admin 예외 없이 무조건 본인분만 표시 (요청이 "다른 사람 것 안 보이게"로 명확했음)
- 결재가 필요한 문서(타인이 상신 + 나에게 결재 요청된 건)는 별도의 **결재함**(`renderApproveBox`, `goTab('approve')`)에서 그대로 처리 가능 — 이 탭은 영향 없음, 확인 완료

### 검증
- `node --check`로 모듈 스크립트(.mjs 추출) 문법 검증 통과
- 대표님 지시로 테스트서버 생략, **본섭 직접 배포**

### 운영 커밋
- production: `edoc/index.html` `a6893b9`, `index.html`(버전주석) 
- 백업: `backup/v2.6.2/edoc/index.html`
