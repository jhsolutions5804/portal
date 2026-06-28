# 2.7. 인사 — 연차 현황

> Firestore: `workers` + `edoc_leave`
> 최초 작성: 2026-06-26 · 최종 수정: 2026-06-29(r2) · 작성: 춘식이(Claude)

---

## 기능 개요

- 전체 직원 연차를 표로 조회 (사번 오름차순)
- 컬럼: 이름 · 부서 · 직급 · 최초 입사일 · 산정 기준 · 부여 · 사용 · 잔여
- 행 클릭 → 근로자 상세 모달 (`showLeaveDetail`)
- 좌측 상단 `🏠 인사 홈` 버튼 (homeBtn)

---

## 근로기준법 연차 계산 (`hrCalcAnnualLeave`)

| 근속 | 부여 일수 |
|------|---------|
| 1년 미만 | 1개월 개근당 1일 (최대 11일) |
| 1년 이상 | 15일 |
| 3년 이상 | `15 + floor((years-1)/2)` (최대 25일) |

- 입사일 미등록 → 부여/잔여 `-` 표시
- 사용일수: **posted 또는 approved** 연차신청서만 집계

> ⚠️ edoc·hr 양쪽에 동일 로직 중복 — 변경 시 양쪽 동시 수정 필요

---

## 근로자 상세 모달 (`showLeaveDetail`)

```js
window.showLeaveDetail(wid, wname, hireDate)
```

- 부여/사용/잔여 요약 카드
- 연차 사용 내역: 일자·종류·일수·상태

---

## 관리자 연차 등록/수정/삭제 (B2, c142acb8)

- **등록 버튼**: 관리자 계정에서만 표시 (`window._isAdmin`)
- **저장**: `edoc_leave` 컬렉션, `adminCreated: true`, `status: 'posted'`
- **폼**: 근로자 선택, 휴가 종류, 시작일/종료일, 일수, 메모
- **수정 버튼**: 상세 모달 내 각 내역 행에 표시

| 함수 | 역할 |
|------|------|
| `openLeaveAdminForm(docId?)` | 등록/수정 폼 열기 (docId 있으면 수정) |
| `saveLeaveAdmin()` | 저장 (신규/수정 공통) |
| `deleteLeaveAdmin(docId)` | 삭제 후 모달 닫기 + 화면 갱신 |
