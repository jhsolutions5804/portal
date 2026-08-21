# 7.28 — 공사일보(daily-report) 저장 실패 근본 원인 수정: Firebase Auth 초기화 누락 (v2.4.1)

**날짜**: 2026-08-21
**대상**: `daily-report/index.html` (FAB)

## 배경
대표가 공사일보 작성 화면에서 저장 버튼을 눌러도 "저장 실패: Missing or insufficient permissions." 알림이 뜬다며 스크린샷 첨부. 명일 예정 작업·기술인 투입 현황·사용 장비·특이사항까지 다 입력한 상태에서 저장만 항상 실패하는 상황.

## 조사
- `daily-report/index.html`의 Firebase 초기화 블록 확인 → `firebase-app.js`, `firebase-firestore.js`만 import, **`firebase-auth.js` import 및 `getAuth()` 호출이 전혀 없음**을 발견
- 비교 대상으로 `pjt/index.html`, `edoc/index.html`, `hr/index.html`, `gihoek/index.html`을 모두 확인 → 4개 모듈 전부 `firebase-auth.js` import + `getAuth(app)` 호출 패턴을 가지고 있음. `daily-report`만 예외
- 코드 내 기존 주석(490번째 줄, 4.5.1에서 남긴 것)에 "standalone 창은 메인 포털 Auth 컨텍스트가 없어 Firestore 조회가 실패할 수 있음"이라는 힌트가 이미 있었음 — 당시엔 조회(portal_users) 실패만 완화 처리했고, 근본 원인(Auth SDK 자체 미초기화)은 손대지 않았던 것으로 확인
- `daily-report/index.html`을 여는 경로는 `pjt/index.html`의 "📋 공사일보" 버튼(`window.open`)뿐이며, 이 버튼은 절대 URL(`https://jhsolutions5804.github.io/portal/daily-report/`)을 가리킴. GitHub Pages 커스텀 도메인 리다이렉트로 `portal.jhsol.kr` 오리진으로 열리는 것을 확인 → 오리진 자체는 메인 포털과 같지만, **iframe/새 탭 등 별도 JS 실행 컨텍스트에서는 Firebase Auth SDK를 그 페이지 안에서 직접 초기화해야만** 로그인 토큰이 Firestore 요청에 실린다는 사실을 재확인 (같은 브라우저·오리진이라도 자동 상속되지 않음)

## 구현
- `firebase-auth.js`에서 `getAuth`, `onAuthStateChanged` import 추가
- `const auth = getAuth(app);` 추가
- `pjt/index.html`과 동일한 접근 게이트 패턴 이식:
  - 전체화면 오버레이(`_access-gate`)로 로딩 중 화면 차단
  - `onAuthStateChanged`로 로그인 여부 확인 → 미로그인 시 안내 문구 표시 후 차단
  - 로그인 되어 있으면 `portal_users/{uid}` 조회 → `status==='approved' && (admin===true || perms.pjt===true)` 확인 → 통과 시에만 오버레이 제거하고 화면 사용 허용
- 공사일보 작성 권한 기준은 대표 확인 하에 **PJT 권한(`perms.pjt`)과 동일하게** 통일 (전용 권한 키 신설은 보류)

## 권한 확인 (요청 사항)
- 수정 전에는 `daily-report/index.html` 자체에 권한 검증 로직이 없었음 — 실질적으로는 `pjt/index.html`의 "공사일보" 버튼이 PJT 권한자에게만 노출되는 것으로 간접 제한되고 있었으나, 직접 URL 접근 시 미승인 계정도 화면 진입 자체는 가능했던 허점 존재 (저장은 Auth 부재로 어차피 실패)
- 이번 수정으로 daily-report 자체에도 PJT 권한 게이트가 생겨 URL 직접 접근 시나리오도 함께 차단됨

## 검증
- `<script type="module">` 블록 추출 → `node --check` 문법 검증 통과
- portal-test(`jhsolutions5804.github.io/portal-test/daily-report/`)에 우선 배포 → 대표 실 테스트로 정상 저장 확인
- 프로덕션 배포 후 파일 내용 재조회하여 배포본이 로컬 패치본과 완전히 일치함을 확인

## 남은 작업
- **`daily-report/ph4.html`(SUP)도 동일한 Firebase Auth 초기화 누락 버그 확인됨 — 아직 미수정.** 다음 세션에서 동일 패턴으로 수정 필요
