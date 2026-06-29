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
