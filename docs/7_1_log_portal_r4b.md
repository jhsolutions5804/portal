# 7_1_log_portal r4b
> 이전 내용: 7_1_log_portal_r4a.md

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

## Test Server 구축 (`2026-06-29`)

### 저장소
- `jhsolutions5804/portal-test`
- GitHub Pages: `https://jhsolutions5804.github.io/portal-test/`

### 구성
- v1.0.5 코드 기반으로 초기화
- 상단 빨간 배너(`⚠️ TEST SERVER`) 추가
- Firebase 프로젝트 동일 (`p4ph2-fab-506a7`)

### 업로드 파일 (초기 커밋)
| 파일 | 커밋 SHA |
|------|---------|
| `index.html` | `78a5becf` |
| `hr/index.html` | `e352c3d3` |
| `gihoek/index.html` | `1693259e` |
| `outlook-auth.html` | `5be7b17e` |
| `edoc/index.html` | `afd4135f` |
| `pjt/index.html` | `4a59d32b` |

### 업데이트 절차 확정
- 기존: local test → main 바로 배포
- 변경: local test → test server 검증 → main 배포
- 상세: `docs/0_ground_rule_r8.md` 참조
- 알고리즘 문서: `docs/0_update_algorithm.md`

---

## Outlook OAuth2 PKCE 연동 현황 (2026-06-29)

### 구현 완료
- MSAL 라이브러리 완전 제거 (CDN 의존성 0)
- `crypto.subtle.digest('SHA-256')` 직접 사용
- `outlook-auth.html` — Microsoft OAuth2 redirect 수신 전용 페이지
- Azure AD 앱: Redirect URI `outlook-auth.html` 등록 완료

### 현재 상태
Azure AD 앱 등록 및 코드 구현 완료. 실제 메일 로드 여부 미확인.

---

## 업데이트 절차 변경 (2026-06-29 확정)

| 구분 | 변경 전 | 변경 후 |
|------|--------|--------|
| 배포 흐름 | local test → main 직접 배포 | local test → test server → main 배포 |
| test server | 없음 | `portal-test` (v1.0.5 기반) |
| 긴급 hotfix | 자유 배포 | 사용자 명시 승인 필요 |

### 문서
- `docs/0_update_algorithm.md` — 9단계 알고리즘 + 체크리스트
- `docs/0_ground_rule_r8.md` — 서버 정보 + 절차 반영

---

## 오늘(2026-06-29) 전체 작업 요약

### 완료 항목
| 코드 | 작업 | 파일 |
|------|------|------|
| J1~J6 | MD 정리, gihoek 홈버튼, _isAdmin, 퇴직금, 여백 | hr, gihoek |
| K1~K3 | 급여명세서 오류, empNo 정렬, Outlook OAuth2 | hr, portal |
| L1~L3 | CDN 교체, 역방향 연동, oninput 수정 | hr, portal |
| M1 | 근로자 명부 수정 → portal 동기화 | hr, portal |
| M2 | gihoek 무한 로딩 수정 | gihoek |
| M3 | 급여명세서 공제내역 직접 수정 + 조회 보존 | hr |
| — | Test server 구축 (portal-test) | — |
| — | Ground Rule r8 + 알고리즘 문서 | docs |

### 백업
- `backup/v1.0.4` — 오전 작업분
- `backup/v1.0.5` — 오후 작업분 (최종)

---

## 2026-06-30~07-01 세션 — PC레이아웃·자동연동·캐시방지 + main 이식

> Test server(`portal-test`)에서 전 작업 무결점 테스트 후 main 일괄 이식

### N11 — iframe 캐시 방지 (portal index.html)
- 포털이 하위 앱(gihoek/edoc 등)을 iframe 로드 시 `src`에 `_cb=Date.now()` 파라미터 추가 → 항상 최신 버전 로드
- iframe src에만 적용, "새 창에서 열기" href는 깔끔하게 유지
- 같은 앱 내 탭 전환(postMessage 분기)은 재로드 없이 유지 (`_embUrl`은 `_cb` 없는 순수 URL로 비교)
- 배경: 테스트 중 "배포했는데 캐시 때문에 안 보임"이 반복 발생 → 매번 최신 방식 채택

### 이번 세션 전체 작업 (코드 N2~N11)
| 코드 | 파일 | 내용 |
|------|------|------|
| N2/N4/N5/N6-1~6/N7/N8/N9 | edoc | PC레이아웃·결재함 서브탭·업무일지 권한·테이블화·홈버튼·뒤로가기 |
| N10-1 | gihoek | 지급예정서 지급완료 → 용역비 직접비 자동연동 |
| N10-2 | gihoek | 급여 PJT 비율배분 (netPay·명세서 월선택·급여일 지정) |
| N11 | portal | iframe 캐시 방지 |

### Main 이식 (2026-07-01)
| 파일 | 커밋 SHA | 이식 전 백업 SHA |
|------|---------|----------------|
| `index.html` | `bf21fa0d` | `2621fe19` |
| `edoc/index.html` | `3a5ad393` | `77d78594` |
| `gihoek/index.html` | `beefbb1c` | `000011fc` |

- `index.html` 이식 시 test 전용 요소 변환: TEST SERVER 배너 제거, 하위앱 URL `portal-test/`→`portal/` (8건), N11 캐시방지는 유지
- `edoc`/`gihoek`은 test 전용 요소 없어 그대로 이식
- `hr/index.html`은 main=test 동일하여 미변경
- 안전성: main 최근 변경(6/29까지)이 모두 test에 포함된 superset 확인 → 이식 시 손실 없음

### 대기열 잔여
- **N1**: Outlook 연동 (Azure AD SPA 플랫폼 미등록 또는 redirect URI 불일치 의심) — 보류

---

## 2026-07-01 세션 — 홈 하이브리드 + 테스트 서버 DB 격리 (인프라)

### 포털 index 기능 (4.3.0 이식)
- PJT 홈 하이브리드 레이아웃(`pjt-cards-row` 2열 + `pjt-timeline-grid` 2단)
- 메뉴명 실시간 반영 `syncPjtSubtabsFromSettings` (로그인 시 `pjt_settings` 읽어 `PJT_SUBTABS` 갱신)
- `window._db=db` 전역 노출 → 홈 일정/보고 패널 "DB 연결 안 됨" 해결
- 업무지시·보고 빈 항목 미표시
- main 이식 커밋 `a613673755` (TEST 배너 제거 + `portal-test/`→`portal/` 8건 치환)

### 테스트 서버 DB 격리 (진행 중) — ⚠️ 중요

**문제**: 기존 테섭(`portal-test`)이 본섭과 **동일 Firebase(`p4ph2-fab-506a7`)** 를 공유 → 테섭에서 승인·입력 시 본섭 운영 데이터 오염 (전자결재 승인이 본섭에 반영되는 사고 확인)

**조치 (A안 — 완전 격리)**:
1. 신규 Firebase 프로젝트 `portal-test-6e0ff` 생성 (Firestore + Auth 이메일/비번, Spark 요금제)
2. 본섭→테섭 Firestore 전체 복제 — Admin SDK 스크립트(`copy_firestore.py`) 로컬 실행. 최상위 컬렉션 자동 나열(동적 포함) + 서브컬렉션 재귀, 429 할당량 시 무한 재시도·이어하기
3. 복제 완료 후 테섭 6개 HTML(`edoc·gihoek·hr·index·pjt·pjt_ph4`)의 `firebaseConfig`를 `portal-test-6e0ff`로 교체 예정 (로컬 준비 완료, 배포 대기)

**교체 매핑**: apiKey/authDomain/projectId/storageBucket/messagingSenderId/appId 6종
**미완**: 데이터 복제 진행 중(무료 할당량으로 수일 소요 가능) → 완료 후 config 교체 배포 + 테스트 로그인 계정 생성

### 이미 섞인 데이터
- 격리 전 테섭에서 발생한 본섭 반영분은 구분 불가로 그대로 둠 (사용자 판단)
