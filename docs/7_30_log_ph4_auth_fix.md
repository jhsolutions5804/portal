# 7.30 — 공사일보(SUP) ph4.html Firebase Auth 초기화 누락 수정, 프로덕션 배포 (v2.4.1)

**날짜**: 2026-08-22
**대상**: `daily-report/ph4.html` (SUP)

## 배경
8/21 세션에서 FAB(`daily-report/index.html`)의 저장 실패 원인(Firebase Auth 초기화 누락)을 수정하면서, 동일 구조인 SUP(`ph4.html`)도 같은 버그가 있는 것을 확인했음. 당시엔 FAB 배포를 마무리하는 게 우선이라 SUP 수정은 portal-test에만 배포해두고 프로덕션은 보류한 상태였음.

## 구현
- FAB에 적용했던 패턴을 `ph4.html`에 그대로 이식: `firebase-auth.js` import + `getAuth(app)` + 접근 게이트(`_accessGatePromise` — 로그인 확인 → `portal_users` 권한 확인, PJT 권한(`perms.pjt`) 기준 동일 적용)
- FAB/SUP 두 파일은 구조가 완전히 동일(같은 Firebase 초기화 블록, 같은 함수명 패턴)해서 patch도 100% 동일하게 적용됨

## 검증
- 프로덕션 배포 직전, 배포 대상 파일(`ph4_prod.html`)과 배포 시점 프로덕션 원본을 diff로 재확인 — Auth 초기화 블록 추가 외 의도치 않은 변경 없음을 확인
- `node --check` 문법 검증 통과
- **portal-test에서의 실 사용자 테스트는 별도로 진행하지 않고 바로 프로덕션 배포함** — FAB에서 동일 패턴이 이미 실사용 검증됐고, SUP 파일 구조가 100% 동일해서 대표 승인 하에 생략

## 배포
- `daily-report/ph4.html` (v2.4.1)
- 버전 코멘트 갱신 (`daily-report(SUP) 2.4.1`)
- 백업: `backup/v2.4.1/daily-report/ph4.html`
- 기능 문서: `docs/4_2_pjt_sup.md`
