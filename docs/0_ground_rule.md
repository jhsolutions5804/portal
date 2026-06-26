# 0. Ground Rule & 용어 정의

> JH Solutions 업무 포털 — 개발·운영 기준 문서
> 최초 작성: 2026-06-26 · 작성: 춘식이(Claude)

---

## 개발 GROUND RULE (필수 준수)

1. 사용자가 지시하는 업무는 모두 **대기열에 등록**한다.
2. 대기열 과제는 반드시 **local에서 무결점 test를 먼저** 시행한다.
   → local test 이상 없으면 **mock-up(HTML format) test를 추가 진행**한다.
   → mock-up test까지 이상 없음을 사용자에게 보고하고, **승인을 받은 후** 배포한다.
3. 기존 시스템과 충돌 없이 정상 구동되는지 여부를 **사용자에게 보고**한다.
4. 모든 publish(GitHub 배포)는 보고 후 **사용자의 지시를 받고** 진행한다.
   → 절대 보고 없이 임의 배포하지 않는다.
5. 수정·배포가 진행될 때마다 **관련 기능 문서(1.x~6.md)와 개발 로그(7.x.md)를 함께 GitHub(`docs/`)에 업로드**한다.
   → 프로젝트 파일이 항상 최신 상태를 유지하도록 문서·코드·로그를 동시에 반영한다.
   → **반드시 `/mnt/user-data/outputs/`에도 해당 `.md` 파일을 출력**하여, 사용자가 로컬에 다운로드 후 다음 대화에서 Claude에 업로드할 수 있도록 한다.
   → 출력 파일명 규칙: `{번호}_{파일명}.md` (예: `7.4_log_edoc.md`)

---

## 기술 원칙

- **배포 전 항상 최신 SHA 확인**: GitHub Contents API PUT 전 반드시 GET으로 현재 SHA를 fresh하게 가져올 것
- **배포 방식**: Python `urllib` + GitHub Contents API PUT (base64 인코딩)
- **JS 문법 검증**: 배포 전 `node --check 파일.html` 필수
- **백틱/달러 이중 이스케이프**: Python heredoc 삽입 시 바이트 치환 필수
  ```python
  content.replace(b'\\`', b'`').replace(b'\\$', b'$')
  ```
- **window 전역 등록**: `<script type="module">` 내 모든 onclick 대상 함수는 `window.fn = fn` 등록 필수
- **실시간 동기화**: Firestore `onSnapshot` 사용 (localStorage 사용 금지)
- **탭 방식 확장**: 별도 페이지 생성 없이 탭으로 기능 추가

---

## 용어 정의

| 용어 | 정의 |
|------|------|
| **포털** | `portal/index.html` — 로그인·계정관리·메뉴 분기 허브 |
| **앱** | 포털 내 각 업무 영역 (기획·인사·전자결재·PJT 등) |
| **iframe 임베드** | 포털이 각 앱을 iframe으로 불러오는 방식 |
| **via=portal** | 포털 경유 접근 파라미터 (`?via=portal`) |
| **Secondary App** | Firebase 2차 인스턴스 (관리자 세션 유지하며 타 계정 조작 시 사용) |
| **_pw** | `btoa(encodeURIComponent(pw))` 형태로 Firestore에 저장된 비밀번호 |
| **perms** | 앱별 접근 권한 플래그 (`plan·hr·edoc·pjt`) |
| **active** | 유효 상태 (정산·견적 등) |
| **void** | 폐기 상태 |
| **done** | 완결 상태 (정산 청구서 확정) |
| **closed** | 종결 상태 (견적 종료) |
| **posted** | 게시 완료 (전자결재) |
| **FAB** | P4 Ph2 — 귀뚜라미 범양냉방 FAB 현장 |
| **SUP** | P4 Ph4 — 귀뚜라미 범양냉방 SUP 현장 |
| **공수** | 인력 투입량 단위 (1일 = 1공수, 최소 0.5단위) |
| **PAST_PROGRESS_DAILY** | Firestore에 없는 과거 공정 데이터를 코드 상수로 보관 |
| **DOC_CONFIG** | 전자결재 문서별 고정 결재라인 설정 객체 |
| **buildFixedApprovalLine** | DOC_CONFIG 기반 결재라인 자동 생성 함수 |
| **portalUid** | workers 컬렉션에서 portal_users를 연결하는 키 필드 |

---

## 파일 구조 인덱스

| 번호 | 파일명 | 내용 |
|------|--------|------|
| 0 | `0_ground_rule.md` | Ground Rule, 용어 정의 (이 파일) |
| 0.1 | `0.1_portal_concept.md` | 포털 concept, structure |
| 0.2 | `0.2_portal_rule.md` | 포털 기본 rule (디자인·공통 코드) |
| 0.3 | `0.3_portal_auth.md` | 포털 인증 구조 |
| 0.4 | `0.4_structure_index.md` | 구조 인덱스 (전체 앱 경로·URL) |
| 1.x | `1.x_*.md` | 기획 앱 각 탭 |
| 2.x | `2.x_*.md` | 인사 앱 각 탭 |
| 3.x | `3.x_*.md` | 전자결재 앱 각 탭 |
| 4.x | `4.x_*.md` | PJT 관리 각 탭 |
| 5 | `5_org_chart.md` | 조직도 |
| 6 | `6_portal_admin.md` | Portal 관리 |
| 7.x | `7.x_*.md` | 개발 로그 |
