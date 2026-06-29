# 7.1. 개발 로그 — 포털 홈

> `portal/index.html` 변경 이력
> 최초 작성: 2026-06-26 · 최종 수정: 2026-06-29(r4+) · 작성: 춘식이(Claude)

---

## 커밋 이력

| SHA | 날짜 | 내용 |
| `9f30a783` | 2026-06-29 | hotfix: renderOutlookCard 함수 복구 (MSAL 교체 시 삭제) |
| `26bcf5b5` | 2026-06-29 | fix: Outlook MSAL 완전 제거 → OAuth2 PKCE 직접 구현 |
| `bec1d595` | 2026-06-29 | fix: outlook-auth OAuth2 authorization_code+PKCE 직접 구현 |
| `e0d0004b` | 2026-06-29 | fix: rosterLinkPortal portal_users 쓰기 → postMessage 위임 |
| `26ef034f` | 2026-06-29 | feat: outlook-auth.html 신설 — MSAL redirect 전용 처리 페이지 |
| `d4148c9e` | 2026-06-29 | fix: J2 gihoek 홈버튼 통일 + J6 여백 1100px |
| `d878cebf` | 2026-06-29 | fix: J3 _isAdmin수신 + J4 퇴직금empNo정렬 + J5 rt-list-panel연동 |
|-----|------|------|
| `783f99e0` | 2026-06-25 | C안 도메인 통합 — 4개 앱 단일 저장소 마이그레이션 |
| `1cc89682` | 2026-06-25 | 부서 선택 선택사항 + 자동 로그아웃 30분 |
| `05308797` | 2026-06-25 | 계정 생성 부서(optgroup)·직급 드롭박스 추가 |
| `3dfbd4bc` | 2026-06-25 | Portal 관리 신설 — 직원 계정 생성·접근권한, 가입 승인 삭제 |
| `e01ae853` | 2026-06-25 | 전자결재(edoc) iframe 모듈 추가 |
| `e743bcd8` | 2026-06-25 | 사이드바에 전자결재 결재함 메뉴 추가 |
| `dfe662b2` | 2026-06-25 | 레이아웃 — 사이드바-메인 간격 제거 |
| `0f624aa5` | 2026-06-25 | 인사 사이드바에 연차 현황(7) 추가 |
| `43fa1d51` | 2026-06-25 | renderDocMain 전역 등록 — 뒤로가기 버튼 작동 수정 |
| `57473bf4` | 2026-06-25 | 직원 비밀번호 변경 UI 신설 (Secondary App) |
| `6eee2bfa` | 2026-06-25 | _pw 자동 동기화 + 기존 계정 최초 1회 입력 처리 |
| `843f3a40` | 2026-06-25 | 기존 계정 최초 1회 현재PW 입력란 조건부 표시 |
| `2e7c6855` | 2026-06-26 | A4+B6 portal↔workers 계정 연동 |
| `24aeb7e2` | 2026-06-26 | PJT홈 공정률 FAB PAST 상수 합산 |
| `2c934054` | 2026-06-26 | A4+B6 portal↔workers 연동 최종 |
| `3d1bfd16` | 2026-06-26 | PJT홈 레이아웃 재구성 (2단: 카드+패널) |
| `bd76eff8` | 2026-06-26 | 홈 대시보드: 결재함+Outlook 2단 카드 / 메뉴카드 제거 |
| `0a8dc3ec` | 2026-06-26 | fix: MSAL 초기화 타이밍 문제 수정 |
| `45d58bcd` | 2026-06-26 | fix: MSAL ESM dynamic import 방식으로 전환 |
| `26942bcf` | 2026-06-26 | fix: MSAL uid별 인스턴스 격리 — 계정별 Outlook 독립 연결 |
| `5d51634c` | 2026-06-26 | mobile: 하단 탭바 추가 (PC 네이비 컬러톤) |
| `aa017cc6` | 2026-06-26 | fix: 모바일 탭바 window 전역 등록 누락 수정 |
| `b08087ca` | 2026-06-26 | fix: 모바일 탭바 onclick→addEventListener 방식으로 교체 |
| `8817a2b0` | 2026-06-26 | fix: 모바일 탭바 window.* 경유 호출로 스크립트 격리 문제 해결 |
| `bb4abe85` | 2026-06-26 | fix: PJT홈 모바일 1단 레이아웃 (인라인 grid→CSS 클래스) |
| `da75d677` | 2026-06-26 | fix: PJT홈 D+ 시작일 직접 입력 기능 추가 |
| `1287c3e7` | 2026-06-26 | fix: 모바일 iframe 높이 확보 + via=portal 파라미터 추가 |
| `5f5274de` | 2026-06-26 | fix: overrideUrl에도 via=portal 추가 |
| `1817364c` | 2026-06-26 | fix(C안): overrideUrl via=portal + D+ Firestore 연동 |
| `5b9953d6` | 2026-06-26 | 완결: 모바일 최종 정리 |
| `3d0887d758` | 2026-06-26 | fix: home-dash 좌우 2단 복구 (모바일 CSS 미디어쿼리 이동) |
| `1e8c51a1` | 2026-06-27 | [D2] 정산도우미 흔적 제거 — desc·주석 portal/hr 기준으로 정리 |
| `bdcf8637` | 2026-06-29 | [D4] MODULES url 중복 ?via=portal 제거 — plan/hr/edoc 3곳 |
| `32d7ab26` | 2026-06-27 | [E1] 사이드바 연봉계약서 번호 2→3, 이후 번호 연쇄 수정 |

---

## 모바일 대응 구현 상세 (2026-06-26)

### 하단 탭바 구조
```
#m-bottom-nav (background: var(--navy), height: 58px, position:fixed bottom:0)
  ├── 🏠 홈     → showView('home')
  ├── 📋 결재   → openModule(edoc, 'approve') + 미결재 배지
  ├── 🏗️ PJT   → showPjtHome()
  └── ☰ 더보기  → 슬라이드업 패널 (#m-more-overlay)
```

### 더보기 패널 구조
```
#m-more-panel (background: var(--navy), border-radius: 20px 20px 0 0)
  ├── 내 정보
  ├── 업무 메뉴 (권한별 분기, 서브탭 아코디언)
  ├── 조직도
  ├── Portal 관리 (admin only)
  └── 로그아웃
```

### 핵심 기술 원칙 (이슈 반복 방지)
- 탭바 버튼 이벤트: `onclick` 인라인 금지 → `setTimeout(0)` 후 `addEventListener`
- module 스크립트 함수 접근: 반드시 `window.xxx` 경유
- `me`, `MODULES`, `SUBTABS`: `window.me = getter/setter`, `window.MODULES` 노출 필수
- iframe URL: `overrideUrl` 여부와 무관하게 항상 `?via=portal` 포함

### PJT홈 반응형
- `home-dash`: 모바일 `flex-direction:column` → PC `grid 1fr 1fr`
- `pjt-home-grid`: 모바일 `flex-direction:column` → PC `grid 1fr 360px`
- `#s-app.shown`: 모바일 `max-width` 제거, `overflow-x:hidden`
- `#view-home`: `box-sizing:border-box`, `overflow-x:hidden`

### D+ Firestore 연동
- 저장: `pjt_settings/{p4ph2|p4ph4}` → `{startDate, updatedAt}`
- 포털 읽기: Firestore 우선 → localStorage 폴백
- 포털 저장: `pjtSaveStartDate()` → Firestore + localStorage 동시

---

## 정산도우미 흔적 제거 (D2, 2026-06-27)

- `MODULES` 배열 hr 항목 desc: `'급여·계약·근태 관리 (정산도우미)'` → `'급여·계약·근태·연차 관리'`
- `HR_SUBTABS` 위 주석: `administrator 앱의 HR_TABS 키와 일치` → `portal/hr 앱의 goTab() 키와 일치`
- 인사 앱은 이미 `portal/hr/index.html`로 완전 이식 완료된 상태였으며, 텍스트·주석만 잔존

---

## 사이드바 연봉계약서 번호 수정 (E1, `32d7ab26`, 2026-06-27)

### 변경 내용

`HR_SUBTABS` 배열 내 emoji(번호) 순차 수정.

| 탭 | Before | After |
|----|--------|-------|
| 연봉계약서 | `2` | `3` |
| 초과근로 | `3` | `4` |
| 급여명세서 | `4` | `5` |
| 퇴직금 정산 | `5` | `6` |
| 연차 현황 | `6` | `7` |

### 배경
근로계약서(2)와 연봉계약서(2)가 동일 번호로 중복 표시됨 → 연봉계약서부터 이후 번호 전체 +1 조정.

### 이슈
초기 업로드 시 구버전 베이스 파일을 수정해서 올렸기 때문에 미반영 발생 → GitHub 최신 파일 재다운로드 후 재업로드로 해결.

---

## 주요 이슈 & 해결

| 이슈 | 해결 |
|------|------|
| 직원 상세 `ed-dept`에 guest 부서 누락 | `deptOpts`에 guest 옵션 추가 |
| PJT홈 공정률 0% (PAST 상수 미포함) | `loadPjtStats`에 `FAB_PAST_PROGRESS` 상수 삽입 후 Firestore와 병합 |
| iframe 빈 화면 | `embed-frame-wrap`에 `position:relative` 추가 |
| 배포 SHA 충돌 | 배포 전 반드시 GET으로 최신 SHA 재확인 |
| Outlook "연결 중" 멈춤 | MSAL CDN script 태그 → ESM dynamic import 방식으로 전환 |
| MSAL 중복 initialize | `_msalInitialized` 플래그 → `_msalApps[uid]` 캐싱으로 개선 |
| 계정 전환 시 타 계정 Outlook 노출 | me.uid 기반 MSAL 인스턴스 격리 + 로그아웃 시 캐시 강제 삭제 |
| 모바일 탭바 버튼 미작동 | onclick 인라인 → addEventListener + window.* 경유 호출로 교체 |
| 모바일 PJT홈 화면 밖 넘침 | grid 인라인 style → CSS 클래스 반응형으로 교체 |
| 워크스페이스 iframe 그래픽 깨짐 | 홈탭 CSS가 PC @media 전용 → 모바일 기본값 CSS 별도 추가 |
| D+ 타 기기 미연동 | localStorage → Firestore `pjt_settings` 저장/읽기로 전환 |
| overrideUrl 사용 시 via=portal 미전달 | `(overrideUrl||m.url)+'?via=portal'` 방식으로 통일 |
| home-dash 상하 배치로 복귀 | 모바일 1단 CSS가 미디어쿼리 밖 전역에 선언 → `@media(max-width:899px)` 안으로 이동 |
| 포털 인사 desc에 정산도우미 잔존 | MODULES hr desc 및 HR_SUBTABS 주석 portal/hr 기준으로 수정 |

---

## Outlook 카드 구현 상세 (2026-06-26)

### Azure AD 앱 정보
```
앱 이름:    jhsolutions_portal
Client ID:  97f0a368-a746-42f9-8782-38ac8cc0962c
Tenant ID:  548fcb48-1ab8-4c47-8242-bc098ea80416
권한:       Mail.Read, User.Read (관리자 동의 완료)
```

### 구현 방식
- **MSAL ESM import**: `https://esm.sh/@azure/msal-browser@3.28.0`
- **계정 격리**: `_msalApps[me.uid]` — 포털 uid별 독립 인스턴스
- **sessionStorage 태깅**: `msal_portal_uid_{homeAccountId}` = uid
- **로그아웃 연동**: `doLogout()` → `clearMsalCache()` 호출

### Outlook 카드 상태 3가지
| 상태 | 표시 |
|------|------|
| 미연결 | Microsoft 계정 연결 버튼 |
| 연결됨 (미확인 있음) | 빨강 숫자 뱃지 + 메일 목록 |
| 연결됨 (모두 읽음) | 초록 ✓ 뱃지 + 메일 목록 |


---

## MODULES url 중복 ?via=portal 제거 (D4, `bdcf8637`, 2026-06-29)

MODULES 배열 url에 `?via=portal`이 포함된 상태에서 `openModule`이 한 번 더 추가
→ `?via=portal?via=portal` 이중 파라미터로 hr 앱이 차단 화면 표시.

**해결**: MODULES url에서 `?via=portal` 제거, `openModule`이 단일 추가하도록 통일.

| 모듈 | 수정 전 | 수정 후 |
|------|---------|---------|
| plan | `.../gihoek/?via=portal` | `.../gihoek/` |
| hr   | `.../hr/?via=portal`     | `.../hr/`     |
| edoc | `.../edoc/?via=portal`   | `.../edoc/`   |
## Outlook OAuth2 PKCE 직접 구현 (K3, 2026-06-29)
### 배경
MSAL 라이브러리(`@azure/msal-browser`)가 CDN 동적 import 방식에서 `pkce_not_created`, `crypto_nonexistent` 등 오류 발생. CDN 교체(esm.sh→unpkg), UMD 방식, redirect 방식 등 시도 모두 실패.

### 최종 해결 방식
외부 라이브러리 완전 제거 → `crypto.subtle` 브라우저 내장 API로 PKCE 직접 구현.

| 구성 요소 | 내용 |
|-----------|------|
| `outlook-auth.html` | Microsoft OAuth2 redirect 수신 전용 페이지 |
| `oa2GenPKCE()` | `crypto.subtle.digest('SHA-256')` 직접 사용 |
| `oa2Login()` | Authorization Code + PKCE 흐름 시작 |
| `oa2GetToken()` | sessionStorage 토큰 조회 |
| `oa2Logout()` | sessionStorage 토큰 삭제 |

### Azure AD 앱 등록 (Redirect URI)
`https://jhsolutions5804.github.io/portal/outlook-auth.html` (단일 페이지 애플리케이션)

## portal_users ↔ workers 역방향 연동 (L2, `e0d0004b`, 2026-06-29)
### 내용
기존: portal_users 등록 → workers 자동 생성 (순방향)
추가: workers 신규 등록(rosterSave) 시 → 이름 매칭으로 portal_users 역방향 연동

### 동작 규칙
- 이름 일치 1건: workers.portalUid + portal_users.workerId/empNo 상호 업데이트
- 이름 일치 0건: workers만 등록 (연동 생략)
- 동명이인(2건+): 연동 건너뜀 (안전 처리)
- portal_users 쓰기 권한 이슈 → `postMessage`로 portal에 위임

## hotfix: renderOutlookCard 복구 (`9f30a783`, 2026-06-29)
MSAL→OAuth2 교체 중 `renderOutlookCard` 함수 본체(98줄) 삭제 → 포털 접속 불가.
정상 커밋(`8115c528`)에서 복원 후 `oa2GetToken` 참조로 교체.

## gihoek 무한 로딩 수정 (`63a82b89`, 2026-06-29)
### 원인
- 이전 세션에서 삽입된 "자동장부 등록" 블록이 `document.write()` 백틱 리터럴 안에 끼어들어 SyntaxError 발생
- `?via=portal` 시 `startApp()` 내 Firestore 쿼리가 미인증 상태에서 블로킹

### 수정
- 오염 블록(49줄) 완전 제거
- `?via=portal`이면 splash 즉시 제거 → `onAuthStateChanged` 안에서 인증 후 onSnapshot 등록
