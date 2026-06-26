# 7.3. 개발 로그 — 인사 앱

> `portal/hr/index.html` 변경 이력
> 최초 작성: 2026-06-26 · 최종 수정: 2026-06-27 · 작성: 춘식이(Claude)

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
| `668d253f` | 2026-06-27 | [D1] hr 내부 사이드바 완전 제거 |
| `6c236d60` | 2026-06-27 | [D2] 근로자 명부 PC 레이아웃 + portal_users 드롭다운 연동 |

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

### 연차 상세 모달 (B1) / 관리자 연차 CRUD (B2)
- 행 클릭 → `showLeaveDetail` 모달
- 관리자 직접 등록: `edoc_leave`에 `adminCreated:true`, `status:'posted'`

### 갑 서명/도장 (B4)
- `company_settings/signatures.kjh` — base64 이미지 저장
- 근로계약서·연봉계약서 A4 출력 시 자동 삽입

### hr 내부 사이드바 완전 제거 (D1)
- 포털 메인 사이드바가 이미 내비게이션 제공 → hr 앱 자체 사이드바 중복
- `<aside id="hr-sidebar">` HTML 블록 + 관련 CSS 전체 삭제

### 근로자 명부 PC 레이아웃 + portal_users 연동 (D2, 2026-06-27)

**변경 내용**

| 항목 | 이전 | 이후 |
|------|------|------|
| 진입 화면 | 등록/조회 선택 버튼 | 명단 테이블 바로 표시 |
| 등록 버튼 위치 | 선택 화면 내 | 목록 우측 상단 독립 배치 |
| 레이아웃 폭 | 모바일 폭(~600px) | PC 폭(max-width:1100px) 테이블 |
| 테이블 컬럼 | 6열(격자) | 11열(사원번호~포털연동·삭제) |
| 신규 등록 폼 | 직접 입력만 | portal_users 드롭다운 + 자동 채움 |
| portalUid 저장 | 없음 | workers 문서에 함께 저장 |

**신규 함수**
```js
loadPortalUsers()           // portal_users 로드 & 캐시
rosterPortalUserSelect(uid) // 드롭다운 선택 → 폼 자동 채움
renderRosterRegister()      // 등록 폼 (portal 연동 UI 포함)
renderRosterList()          // renderRosterMain()으로 리다이렉트
```

**포털 연동 드롭다운 로직**
1. `portal_users` 전체 로드 (empNo 오름차순)
2. `workers` 내 `portalUid`가 이미 있는 uid 제외
3. 잔여 계정만 드롭다운으로 표시
4. 선택 시 이름·직급·부서 자동 채움 + 초록 피드백 메시지 표시

---

## 이슈 & 해결

| 이슈 | 해결 |
|------|------|
| Firebase config messagingSenderId 0 추가로 Auth 오류 | 원본 11자리로 복원 |
| hr 앱 내부 사이드바 포털과 중복 표시 | 사이드바 HTML·CSS 완전 제거 |
| 명부 탭 진입 시 모바일 환경 렌더 | PC 테이블 레이아웃(max-width:1100px)으로 교체 |
| 신규 등록 시 portal 연동 정보 수동 입력 불편 | portal_users 드롭다운 + 자동 채움 기능 추가 |
| 이미 연동된 portal 계정이 드롭다운에 노출 | workers.portalUid 조회 후 제외 처리 |
