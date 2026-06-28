# 7.3. 개발 로그 — 인사 앱

> `portal/hr/index.html` 변경 이력
> 최초 작성: 2026-06-26 · 최종 수정: 2026-06-27(r8) · 작성: 춘식이(Claude)

---

## 커밋 이력

| SHA | 날짜 | 내용 |
|-----|------|------|
| *(초기)* | 2026-06-24 | 7개 탭 구성 |
| `668d253f` | 2026-06-27 | [D1] hr 내부 사이드바 제거 |
| `6c236d60` | 2026-06-27 | [D2] 명부 PC 레이아웃 + portal_users 드롭다운 |
| `755521e6` | 2026-06-27 | [D3] 명부 v3 전면 개선 |
| `4037f6e3` | 2026-06-27 | [fix1] modal 중첩 백틱 + calcWorkDays 복원 |
| `a31763f1` | 2026-06-27 | [fix2] md 기준 명부 전면 정합 |
| `9b9f4abc` | 2026-06-27 | [E1] 연봉계약서 PC 테이블 레이아웃, 사원번호 순 정렬 |
| `620abd6c` | 2026-06-27 | [D4] getWorkersList empNo 단일 정렬 통일 |
| `3c9b1942` | 2026-06-27 | [D3] 근로계약서 PC 테이블 재배포 |
| `d88ee9b4` | 2026-06-27 | [F1] 초과근로 PC 레이아웃 복구 |
| `fd0e3313` | 2026-06-27 | 포털 전용 접근 — denied 차단 화면 |
| `d00296de` | 2026-06-27 | [G1] 급여명세서 PC 레이아웃 |

---

## [fix2] md 기준 명부 전면 정합 (`a31763f1`, 2026-06-27)

### 배경
md 파일(`2_1_hr_roster_r4`)과 실제 배포 코드를 항목별 비교한 결과, 51개 점검 항목 중 다수가 구버전 코드로 남아있음을 확인. 명부 섹션 전면 재작성.

### 누락됐던 항목 (이번에 적용)

| 항목 | 이전 | 이후 |
|------|------|------|
| `portalUid` workers 저장 | ❌ | ✅ rosterSave에 명시 저장 |
| `signData` workers 저장 | ❌ | ✅ rosterSave null 초기화·rosterDetailSave 저장 |
| `➕ 신규 등록` 버튼 | ❌ 구버전 selectMain | ✅ 우측 상단 독립 버튼 |
| 포털 열 🔗/미연동 | ❌ | ✅ |
| portal_users 드롭다운 | ❌ | ✅ reg-portal-select |
| `rosterRegPortalSelect` | ❌ | ✅ |
| `rosterDetailSave` portal_users 역방향 동기화 | ❌ | ✅ name·rank·dept |
| `rosterEmpNoCancel` | ❌ | ✅ |
| `rosterEmpNoSave` empNo 역방향 동기화 | ❌ | ✅ portal_users.empNo |
| 신규 등록 시 portal_users.empNo 동기화 | ❌ | ✅ |
| 서명 패드 (rosterOpenSignPad 등) | ❌ | ✅ canvas 380×120 |
| `window.getWorkerData` | ❌ | ✅ 전역 등록 |
| `renderRosterList → renderRosterMain` | ❌ | ✅ |

### 유지된 항목
- `KR_HOLIDAYS` + `calcWorkDays` 위치 (rosterDetail 앞)
- 중첩 백틱 없음 (문자열 연결 방식 사용)
- 사번 자동 부여 (yy+padStart(3,'0'))
- `rosterDelete` confirm + deleteDoc

---

## 이슈 & 해결

| 이슈 | 원인 | 해결 |
|------|------|------|
| 상세 모달 열리지 않음 | modal.innerHTML 중첩 백틱 | 문자열 연결 방식으로 교체 |
| 재직기간 0 표시 | D3 교체 시 calcWorkDays 누락 | 원본 복원 |
| 대부분 기능 미반영 | D3 배포 시 old 코드가 섹션에 잔존 | fix2에서 md 기준 전면 재작성 |

---

## 연봉계약서 개편 (E1, `9b9f4abc`, 2026-06-27)

### 변경 내용

**1. renderAnnualMain — PC 테이블 레이아웃**

| 항목 | Before | After |
|------|--------|-------|
| 진입 화면 | 등록/조회 카드 선택 (`selectMain`) | PC 테이블 직접 표시 |
| max-width | 840px (`wrap2`) | 1100px (근로계약서 동일) |
| 신규 작성 | 카드 클릭 | 우측 상단 ➕ 버튼 |
| 상세 진입 | 별도 목록 → 선택 2단계 | 이름 클릭 or 조회 버튼 1단계 |
| 컬럼 | — | 사원번호·이름·소속·직급·구분·최신계약일·계약수·상태·조회 |

**2. 사원번호 순 정렬**
- `workers` 배열 `empNo` 기준 `localeCompare` 정렬 후 렌더링

**3. renderAnnualList2 래퍼 통합**
- 기존 `renderAnnualList2` (별도 조회 목록) 제거
- `window.renderAnnualList2 = () => renderAnnualMain()` 래퍼로 교체 (기존 참조 호환 유지)

### 상태 표시 로직
```
유효 계약: ✅ YYYY년 MM월 DD일 (초록 #16A34A)
만료 계약: ⚠️ 만료 (빨강 #DC2626)
미작성:    미작성 (회색 #9AAABF)
```

### 이슈 & 해결

| 이슈 | 원인 | 해결 |
|------|------|------|
| 코드 수정 후 GitHub 미반영 | 구버전 베이스 파일을 수정해서 업로드 — 그 사이 변경된 커밋 덮어씌워짐 | GitHub 최신 SHA 재확인 후 최신 파일 새로 다운로드·수정·재업로드 |
| renderAnnualList2 제거 후 닫는 `};` 잔존 | str_replace 범위 지정 미스 | 잉여 `};` 별도 str_replace로 제거 |

---

## r7 이후 누락 커밋 보완 (`620abd6c` ~ `fd0e3313`, 2026-06-27)

### [D4] getWorkersList empNo 단일 정렬 (`620abd6c`)
- 기존: `name` 기준 sort가 `empNo` sort를 덮어쓰는 버그 존재
- 수정: `getWorkersList` 내 `empNo` localeCompare 단일 정렬로 통일

### [D3] 근로계약서 PC 테이블 재배포 (`3c9b1942`)
- `renderLaborMain` 진입 시 바로 근로자 목록 테이블 표시
- 신규 작성·조회 버튼 상단 배치

### [F1] 초과근로 PC 레이아웃 복구 (`d88ee9b4`)
- `innerWidth >= 900` 분기 — `renderOvertimePC` / `renderOvertimeMobile`
- PC: KPI 바(4열) + 좌패널(직원목록·입력폼) + 우패널(상세내역)

### 포털 전용 접근 (`fd0e3313`)
- Firebase Auth 유지, `portal_users` 컬렉션 권한 확인
- 미등록 사용자 → `denied-card` 차단 화면 표시

---

## 급여명세서 PC 레이아웃 (G1, `d00296de`, 2026-06-27)

### 변경 내용

**PC/모바일 분기 (`PS_PC_BP = 900`)**

| 항목 | Before | After |
|------|--------|-------|
| 진입 | 작성/조회 카드 선택 (`selectMain`) | PC: 바로 작성 화면 / 모바일: 기존 유지 |
| 작성 레이아웃 | 단일 컬럼 카드 스택 | 좌(260px) + 우(flex:1) 2단 |
| 지급/공제 표시 | 순차 카드 | 좌우 **2열 grid** 동시 표시 |
| 조회 레이아웃 | 근로자 목록 → 월 목록 2단계 탐색 | 좌(240px) + 우 카드 그리드 1단계 |

**신규 함수**

| 함수 | 역할 |
|------|------|
| `renderPayslipPC()` | PC 작성 뼈대 + 핸들러 등록 |
| `renderPayslipPCRight()` | PC 우패널 계산값 렌더 (재호출용) |
| `renderPayslipPCList()` | PC 조회 뼈대 |
| `psLoadWorkerSlips(wid, wname, btn)` | PC 조회 우패널 월별 카드 로드 |
| `psDeleteSlipPC(wid, mid, wname)` | PC 삭제 후 우패널 갱신 |
| `psPcMonthChange(month)` | 기준월 변경 → 초과근로 재연동 |
| `psPcWorkerSelect(wid)` | 근로자 선택 → 연봉계약서 로드 |

**모바일 기존 함수 완전 유지**
- `renderPayslipWrite`, `renderPayslipWriteForm`, `renderPayslipListNew`,
  `psWorkerSelect`, `psViewWorker`, `psViewDetail`, `psDeleteSlip`

### 이슈 & 해결

| 이슈 | 원인 | 해결 |
|------|------|------|
| PC 레이아웃 미표시 | `tab-content`가 `display:block`이라 `height:100%;flex:1` 방식 부모 높이 없음 | `max-width:1100px;margin:0 auto` 스크롤 방식으로 전환 (초과근로 동일 패턴) |
| `calcPayDateGlobal` 코드 파손 | str_replace 범위 지정 미스로 함수 본문이 `psDeleteSlipPC` 안에 삽입됨 | 파일을 3분할(head/새코드/tail) 후 재합산 |
