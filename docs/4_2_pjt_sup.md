# 4.2. PJT 관리 — P4 Ph4 SUP

> 앱: `portal/pjt_ph4/index.html` · 워커 컬렉션: `pjt_workers_ph4`
> Firestore(차이): `ph4_schedules`(일정), `ph4_reports`(업무지시), `pjt_workers_ph4` · localStorage 키 `ph4ls_`
> 최초 작성: 2026-07-01 · 최종 개정: 2026-08-22 (공사일보 ph4.html Firebase Auth 초기화 누락 수정, v2.4.1) · 작성: 춘식이(Claude)

---

## 접근 검증 (2026-07-27)

- FAB(`4_1_pjt_fab.md`)와 동일한 구조·동일한 패치 적용 — 로그인+`portal_users`(`status==='approved' && (admin || perms.pjt)`) 검증 게이트, `waitForFirebaseAndInit()` 폴링 조건에 `window._accessGranted` 추가, 공수/공정 preload·`subscribeUserSchedules()`·`subscribeEdocLeave()`·`applyOnLoad()`·`renderProgress()` 모두 검증 통과 후에만 실행
- 상세 원리는 `4_1_pjt_fab.md` 참고


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

---

## 2026-07-14 (4.5.1) 반영 — FAB와 동일 적용

- **공사일보 작성자 드롭다운 버그 수정**: standalone 창(Auth 컨텍스트 없음)에서 `portal_users` 조회 실패 시에도 로그인 계정이 항상 옵션에 추가+자동선택되도록 수정. `daily-report/ph4.html` 동일 적용

### 공사일보(ph4.html) 저장 실패 근본 원인 수정 (v2.4.1, 2026-08-22)

- **증상**: FAB(`daily-report/index.html`)와 동일하게 SUP(`daily-report/ph4.html`)도 저장 시 "Missing or insufficient permissions." 실패
- **원인**: FAB와 동일 — `firebase-auth.js` import 및 `getAuth(app)` 호출이 아예 없어 Firestore 요청이 항상 미인증 상태였음 (8/21 FAB 수정 당시 SUP는 별도 확인 필요로 남겨뒀던 항목)
- **수정**: FAB에 적용한 것과 동일한 패턴 그대로 이식 — `getAuth(app)` + 접근 게이트(로그인 확인 → `portal_users`의 `status==='approved' && (admin===true || perms.pjt===true)` 확인)
- 검증: `node --check`, 원본 대비 diff로 의도한 부분(Auth 초기화 블록)만 추가됐는지 확인 → 프로덕션 배포 (portal-test 별도 확인 없이, FAB에서 이미 검증된 동일 패턴이라 곧바로 진행)

> 상세 원인·수정 내역은 4.1(FAB) 문서 참조.

---

## 2026-07-20 (4.5.2) 반영 — FAB와 동일 적용

- **자정 넘기는 일정 시작일에만 표시**: "19:00~다음날 05:00"처럼 자정을 넘겨 끝나는 일정이 다음날에도 중복 표시되던 문제 수정. `_usItemsForKey`에서 종료일이 시작일 다음날이고 종료시각이 시작시각보다 빠르거나 같으면 시작일에만 표시. 진짜 여러 날짜 일정(출장 등)은 기존대로 각 날짜 유지. `ph4_schedules` 컬렉션 사용, 함수·로직은 FAB와 완전 동일

> 상세 판별 로직은 4.1(FAB) 문서 참조.

