# 7.3. 개발 로그 — 인사 앱

> `portal/hr/index.html` 변경 이력
> 최초 작성: 2026-06-26 · 작성: 춘식이(Claude)

---

## 커밋 이력

| SHA | 날짜 | 내용 |
|-----|------|------|
| *(초기)* | 2026-06-24 | 7개 탭: 홈·명부·근로계약·연봉계약·초과근로·급여·퇴직금 |
| *(Rev2)* | 2026-06-25 | 연차 현황 탭(8번) 추가 |
| `2cf3c6996b` | 2026-06-26 | Firebase config 원본 복원 |
| `af97588c` | 2026-06-26 | 인사 홈 hrShowList 팝업 |
| `6b3d929611` | 2026-06-26 | 인사 홈 연차카드 빈칸 수정 |
| `9eebe9bad5` | 2026-06-26 | 근로자 목록 사번순 정렬 |
| `1f9d685b86` | 2026-06-26 | B1 연차상세 모달 + B2 관리자 연차 CRUD |
| `91adcb481b` | 2026-06-26 | B4 갑 서명/도장 등록·출력 |
| *(미배포)* | 2026-06-26 | C1 직접 접근 인증 portal_users 통일 |

---

## 주요 변경 상세

### Firebase config 오염 복원
- 오염값: `messagingSenderId: '369463179140'` (0 추가)
- 원본: `'36946317914'` (11자리)
- hr + edoc 양쪽 복원

### 인사 홈 연차카드 빈칸 수정 (A3)
- 7번 카드가 `full`(한 줄 전체)로 돼 6번 카드 옆이 비었음
- 7번을 일반 카드로 변경 → 6·7번 나란히 배치

### 근로자 목록 사번순 정렬 (B3)
- 6곳 전체에 `empNo` 기준 정렬 적용
- `(a.empNo||'').localeCompare(b.empNo||'')`

### 연차 상세 모달 (B1)
- 행 클릭 → `showLeaveDetail(wid, wname, hireDate)` 모달
- 요약 카드 + 사용 내역(일자·종류·일수·상태)

### 관리자 연차 CRUD (B2)
- "연차 등록" 버튼 (관리자만)
- `edoc_leave`에 `adminCreated: true`, `status: 'posted'`로 저장
- 함수: `openLeaveAdminForm`, `saveLeaveAdmin`, `deleteLeaveAdmin`

### 갑 서명/도장 (B4)
- `company_settings/signatures.kjh` — base64 이미지 저장
- 근로계약서·연봉계약서 A4 출력 시 자동 삽입
- 관리자 전용 업로드 UI (`renderSignMgr`)

### 직접 접근 인증 통일 (C1)
- 기존: 직접 URL 접근 시 구버전 `allowed_users/{email}` 컬렉션 참조
- 변경: `portal_users/{uid}` 기반으로 통일
- 구버전 컬렉션 `allowed_users`, `access_requests` 참조 제거

---

## 이슈 & 해결

| 이슈 | 해결 |
|------|------|
| Firebase config messagingSenderId 0 추가로 Auth 오류 | 원본 11자리로 복원 |
| renderHome 템플릿 리터럴 내 백틱 중첩 → SyntaxError | DOM 직접 조작 방식으로 우회 |
| 직접 URL 접근 시 allowed_users 미존재로 접근 불가 | portal_users 기반으로 인증 통일 |
