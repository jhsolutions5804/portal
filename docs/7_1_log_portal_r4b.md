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
