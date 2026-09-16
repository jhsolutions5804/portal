# 2.1. 인사 — 근로자 명부

> Firestore 컬렉션: `workers`
> 최초 작성: 2026-06-26 · 최종 수정: 2026-09-16(r6 · 퇴직 처리/재직 복구 기능 추가) · 2026-06-29(r5) · 작성: 춘식이(Claude)

---

## Firestore 스키마

```js
workers/{workerId}:
{
  empNo:       string,    // 가입연도2자리 + 연도순번3자리 (예: 26001)
  name:        string,
  jumin:       string,    // 주민번호 13자리
  phone:       string,
  address:     string,
  dept:        string,
  rank:        string,
  job:         string,
  empType:     'field' | 'office',
  hireDate:    string,    // YYYY-MM-DD
  bankAccount: string,
  portalUid:   string,    // portal_users UID (연동 키)
  signData:    string,    // 개인 서명 base64 (전자결재 연동용)
  registeredAt: string
}
```

**workerId 형식**
- hr 앱 등록: `{이름}_{주민번호13자리}` (예: `홍길동_9001011234567`)
- portal 자동 생성: `{이름}_portal_{uid앞6자리}` (예: `홍길동_portal_abc123`)

---

## 연동 방향 (마스터 정책)

### 순방향 (기존)
`portal_users` 등록 → `workers` 자동 생성 + `portalUid` 저장

### 역방향 (2026-06-29 추가)
`rosterSave()` 완료 후 이름 매칭으로 `portal_users` 자동 연동:
- 1건 매칭 → `workers.portalUid` + `portal_users.workerId/empNo` 상호 업데이트
- 0건/동명이인 → 연동 생략 (안전 처리)
- 권한 이슈: `portal_users` 쓰기는 `postMessage`로 portal에 위임

### 기존 근로자 수동 연동
근로자 명부 상세 모달 하단 **🔗 포털 계정 연동** 버튼 → `rosterLinkPortal()` 호출

```
workers (마스터)
  └→ portal_users 역방향 동기화 (name·rank·dept·empNo)
  └→ 계약서: await window.getWorkerData(workerId)
  └→ 전자결재: signData 로드
  └→ portal 직원 상세: portalUid로 조회 → 읽기 전용 표시
```

---

## 화면 구성 (v3)

- 탭 진입 즉시 **PC 테이블** 직접 표시 (`max-width:1100px`)
- 컬럼: 사원번호 · 이름 · 소속 · 직급 · 구분 · 생년월일 · 휴대폰 · 근로계약 · 연봉계약 · 포털 · 삭제
- 우측 상단 `➕ 신규 등록` 버튼 독립 배치
- 포털 열: 🔗 초록(연동됨) / 회색 `미연동`(미연결)

---

## 주요 기능

### 이름 클릭 → 상세/수정 모달
- 전 필드 수정: 이름·주민번호·휴대폰·주소·계좌·담당업무·소속·직급·구분·입사일
- 저장 시 `portal_users` 역방향 동기화 (portalUid 있을 때)
- 재직기간·실 근무일수 자동 계산 (`calcWorkDays` 사용)

### 사원번호 클릭 → 인라인 수정
- ✓ 저장 / ✕ 취소 버튼
- 저장 시 `portal_users.empNo` 역방향 동기화

### 신규 등록
- `portal_users` 드롭다운 → 이름·직급·부서 자동 채움 + `portalUid` 저장
- 저장 시 사원번호 자동 부여 → `portal_users.empNo` 역방향 동기화
- 포털 미연동: 직접 입력 가능

### 삭제
- 🗑 버튼 → confirm → `deleteDoc` (계약서 데이터 유지)

---

## 개인 서명 (signData)

- 상세 모달 하단 **서명 패드** (canvas 380×120, 마우스·터치 지원)
- 저장 → `workers.signData` (base64 PNG)
- 전자결재에서 `getWorkerData` 호출 시 함께 로드

---

## 계약서 연동 준비

```js
// 전역 등록 함수 — 각 계약서·전자결재에서 호출
const w = await window.getWorkerData(workerId);
// 반환: { name, jumin, phone, address, dept, rank, job, empType,
//         hireDate, bankAccount, empNo, portalUid, signData }
```

---

## 공유 함수 위치 주의

`KR_HOLIDAYS` 상수와 `calcWorkDays` 함수는 **명부 섹션 내부에 위치**.
명부 섹션 코드 교체 시 이 두 함수가 새 코드에도 포함되어 있는지 반드시 확인.

```
// 위치: window.rosterDetail 정의 직전
const KR_HOLIDAYS = new Set([...]);
function calcWorkDays(startStr, endStr) { ... }
```

> 실제 사고 사례(2026-06-27): D3 교체 시 누락 → 퇴직금 탭 파손 + 재직기간 0 표시

---

## 사번 자동 부여

```
empNo = 입사연도 2자리 + 해당 연도 순번 3자리
예) 2026년 첫 번째 → '26001'
```

---

## CRUD 주요 함수
| 함수 | 설명 |
|------|------|
| `rosterSave()` | 신규 등록 + 역방향 portal_users 연동 |
| `rosterDetailSave(id)` | 기존 근로자 수정 저장 |
| `rosterLinkPortal(wid, name)` | 기존 근로자 수동 포털 계정 연동 |
| `rosterDelete(id, name)` | 근로자 삭제 |
| `rosterEmpNoSave(id)` | 사원번호 인라인 수정 |

| 함수 | 역할 |
|------|------|
| `renderRosterMain()` | 목록 테이블 렌더 |
| `renderRosterRegister()` | 신규 등록 폼 |
| `rosterRegPortalSelect(uid)` | 드롭다운 선택 → 폼 자동 채움 |
| `rosterSave()` | 저장 + portal_users 역방향 동기화 |
| `rosterDetail(id)` | 상세/수정 모달 |
| `rosterDetailSave(id)` | 수정 저장 + portal_users 역방향 동기화 |
| `rosterDelete(id, name)` | 삭제 |
| `rosterEmpNoEdit/Save/Cancel(id)` | 사원번호 인라인 수정 |
| `rosterOpenSignPad(id)` | 서명 패드 오픈 |
| `rosterSignSave()` | 서명 저장 |
| `window.getWorkerData(workerId)` | 계약서·전자결재 연동용 전역 함수 |
| `rosterResign(id, name)` | 퇴직 처리 — 퇴직일 입력 후 `status:'resigned'`, `resignDate` 저장 (삭제 아님, 명부에 남고 배지로 표시) |
| `rosterUnresign(id, name)` | 재직으로 복구 — `status:'active'`, `resignDate` 필드 삭제 |

---

## 퇴직 처리 기능 (r6, 2026-09-16)

**배경**: 기존에는 근로자를 명부에서 없애려면 `rosterDelete`(영구 삭제)뿐이었음. 계약서/급여명세서 등 연결 데이터는 유지한 채 "퇴직" 상태만 표시하는 소프트한 방법이 없었음.

**추가 필드**: `workers/{id}`에 `status`('active' 기본값 없음 = active 취급 / 'resigned'), `resignDate`(YYYY-MM-DD) 추가.

**동작**:
- 상세 모달(`rosterDetail`)에 재직중(🟢)/퇴직(🔴, 퇴직일 표시) 배지 및 `🚪 퇴직 처리` / `↩️ 재직으로 복구` 버튼 추가.
- 퇴직 처리 시 `prompt()`로 퇴직일 입력받아 즉시 저장(별도로 "수정 저장" 누를 필요 없음, `rosterDelete`와 동일한 즉시반영 패턴).
- 퇴직 처리된 근로자는 **재직 기간·실 근무일수·퇴직금(예상) 계산의 종료일을 "오늘"이 아닌 "퇴직일"로 고정** — `calcWorkDays(hireDate, resignDate)`.
- 목록(`renderRosterList`)에서 퇴직자는 이름 옆 `퇴직` 배지 + 행 배경 흐리게 처리, 정렬 시 최하단으로 이동(삭제되어 사라지지 않고 계속 조회 가능).

**영향 범위 밖**: `퇴직금 정산`(`renderRetireCalcMobile` 등, 2_6_hr_retire_r2.md)은 기존과 동일하게 퇴직일을 매번 수동 입력하는 별도 플로우로, 이번 `resignDate`와 자동 연동되지 않음(필요 시 추후 연동 검토).

