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
