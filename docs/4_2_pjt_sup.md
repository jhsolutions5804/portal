# 4.2. PJT 관리 — P4 Ph4 SUP

> 앱: `portal/pjt_ph4/index.html` · 워커 컬렉션: `pjt_workers_ph4`
> Firestore(차이): `ph4_schedules`(일정), `ph4_reports`(업무지시), `pjt_workers_ph4` · localStorage 키 `ph4ls_`
> 최초 작성: 2026-07-01 · 최종 개정: 2026-07-08 (4.5.0) · 작성: 춘식이(Claude)

---

## 개요

P4 Ph4 (SUP)는 **P4 Ph2 (FAB)와 동일한 코드 베이스**다. 구조·기능·화면은 4.1 문서(FAB)와 완전히 동일하며, 차이는 다음뿐:

| 항목 | FAB (p4ph2) | SUP (p4ph4) |
|------|-------------|-------------|
| 앱 경로 | `portal/pjt/` | `portal/pjt_ph4/` |
| 워커 컬렉션 | `pjt_workers_fab` | `pjt_workers_ph4` |
| 일정 컬렉션 | `user_schedules` | `ph4_schedules` |
| 업무지시 컬렉션 | `daily_report_docs` | `ph4_reports` |
| localStorage 키 | `fabls_` | `ph4ls_` |
| 현장 | FCU 설치 | EHU 설치 |

---

## 2026-07-02 (4.x) 반영 — FAB와 동일 적용

FAB(4.1)에 추가된 아래 기능이 SUP에도 **동일하게** 반영됨:

- **주간**: 좌우 2주 블록 이동 네비게이터 + `오늘` 버튼
- **캘린더**: 날짜별 일정 등록·수정·삭제(`＋ 이 날 일정 등록`) + 년월 점프(월 선택기)
- **근태**: 전체 출역 일괄 체크/해제(좌) + 전체 공수 일괄 조정(우)
- **일정 등록자 자동 반영**: 로그인 계정으로 등록자 자동 채움 (localStorage `jh_login_full`/`jh_login_name`)

> 상세 동작·함수·스키마는 4.1(FAB) 문서 참조.

---

## 2026-07-08 (4.5.0) 반영 — FAB와 동일 적용

- **공사일보 조회 수정/삭제**: 조회 상세 모달에 ✏️수정 / 🗑삭제 추가. 수정은 `setDoc(merge)`, 삭제는 `deleteDoc`. 현장명·작성일자 고정, 나머지 6개 필드 편집 가능
  - 컬렉션만 차이: SUP는 **`ph4_reports`** (FAB `daily_report_docs`). 함수·UI 동일
- **홈 일정 관리(포털 홈)**: 홈 우측 상세 패널에서 일정 상세·등록·수정·삭제. SUP 일정은 **`ph4_schedules`** 컬렉션에 저장 (상세는 4.0 홈 문서 참조)

> 상세 동작·함수·스키마는 4.1(FAB)·4.0(홈) 문서 참조.
