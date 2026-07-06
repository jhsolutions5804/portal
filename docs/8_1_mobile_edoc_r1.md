# 8.1. 모바일 전자결재 — 작성 · 결재 · 삭제 (r1)

> Firestore 컬렉션: `edoc_daily`, `edoc_leave`, `edoc_overtime`, `overtime`, `workers`, `annual_contracts/*`
> 최초 작성: 2026-07-06 · 작성: 춘식이(Claude) · 릴리스: v2.1.0

---

## 개요

모바일 전자결재(`m/edoc.html`)를 **조회 전용에서 작성·결재·삭제까지** 확장했다. 대표 지정 우선순위 4종: **결재(승인/반려) · 연차신청 작성 · 초과근로신청 작성 · 업무일지 작성**. 나머지(구매품의·지출결의·재직증명·퇴직원서)는 조회만.

- 로그인 정보 `_me` = `localStorage.jh_login_perms`(name·dept·rank·uid·admin). (로그인 게이트는 `0_3` 참조)
- import 확장: doc·getDoc·getDocs·setDoc·addDoc·deleteDoc·serverTimestamp·query·orderBy·limit. `edoc_overtime` 구독 추가.

---

## 결재 (승인/반려)

- **`canApprove(d)`**: 결재선에 `role==='결재' && status==='pending'`인 단계가 있고, 본인이거나 **관리자(admin)면 대행 가능**. 단 **문서 status가 approved/rejected/posted/done이면 false**(이미 완료된 문서는 버튼 숨김).
- **`approveBtns(id,dtype,d)`**: 대기 문서 상세에 승인/반려 버튼 노출.
- **`mobileApprove(docId, dtype, newStatus, docDataStr)`**:
  - 결재선 단계 갱신(내 단계 → approved/rejected; admin이면 대기 결재단계 대행)
  - status 전환: 다음 결재자 있으면 `reviewing`, 없으면 `approved`
  - **초과근로 승인 시 인사 `overtime` 자동 등록 + `linkedToOvertime` 중복방지** (PC와 동일)

## 삭제

- **`canDelete(d)`**: 관리자 OR 작성자 본인 OR **미승인 문서(draft/pending/reviewing)**(상신 취소 허용).
- **`mobileDelete(docId, dtype)`**: `deleteDoc(edoc_{dtype}/{docId})`.

---

## 작성 3종

각 목록 우측 하단 `+` FAB → 작성 폼 → 상신(`status:'pending'`).

| 종류 | 함수 | 컬렉션 | 결재선 |
|---|---|---|---|
| 업무일지 | `renderDailyWrite`/`dailySaveM` | `edoc_daily` | 작성 → 결재 김종화 차장 → 수신 송지훈 대표 |
| 연차신청 | `renderLeaveWrite`/`leaveSaveM` | `edoc_leave` | 작성 → 결재 김종화 차장 → 수신 송지훈 대표 |
| 초과근로 | `renderOvertimeWrite`/`overtimeSaveM` | `edoc_overtime` | 작성 → 결재 김종화 차장 → 회람 김민서 대리 |

- 초과근로: 통상임금 로직 이식(`otCalcAnnualSalary`/`otGetWage`/`otLoadWorkers`), 근로자 선택 시 통상임금·수당 자동. (계산식은 `3_4` 참조)
- 홈 타일에 초과근로 추가. **퇴직원서는 일반 타일(재직증명서 옆)로 배치**(8타일 4×2).

---

## 일자 기준 06시 (PC 통일)

- 작성 기본 일자는 `bizToday()` 사용: **오전 6시 전이면 전날**(`if(getHours()<6) 전날`), 로컬(한국) 시각 기준.
- ⚠️ 기존 `new Date().toISOString().slice(0,10)`은 **UTC**라 한국 날짜와 어긋남 → 사용 금지.

---

## 관련 커밋 (2026-07-06)
과제③ 결재/작성/삭제 → 테섭 검증 → admin 대행·삭제 완화 → 본섭 배포(6eb3c35) → 버그수정(승인완료 버튼숨김·퇴직원서 타일·06시, cccaa0a).
