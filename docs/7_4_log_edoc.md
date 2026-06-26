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
