# 0. Ground Rule & 용어 정의

> JH Solutions 업무 포털 — 개발·운영 기준 문서
> 최초 작성: 2026-06-26 · 최종 수정: 2026-06-27 · 작성: 춘식이(Claude)

---

## 개발 GROUND RULE (필수 준수)

1. 사용자가 지시하는 업무는 모두 **대기열에 등록**한다.
2. 대기열 과제는 반드시 **local에서 무결점 test를 먼저** 시행한다.
   → local test 이상 없으면 **mock-up(HTML format) test를 추가 진행**한다.
   → mock-up test까지 이상 없음을 사용자에게 보고하고, **승인을 받은 후** 배포한다.
3. 기존 시스템과 충돌 없이 정상 구동되는지 여부를 **사용자에게 보고**한다.
4. 모든 publish(GitHub 배포)는 보고 후 **사용자의 지시를 받고** 진행한다.
   → 절대 보고 없이 임의 배포하지 않는다.
5. 수정·배포가 진행될 때마다 **기능 문서(1.x~6.md)와 개발 로그(7.x.md) 모두 업데이트 후 GitHub(`docs/`)에 업로드**한다.
   → 기능 문서: 변경된 스펙·동작·스키마 반영
   → 개발 로그: 커밋 SHA·날짜·변경 내용·이슈 & 해결 추가
   → 둘 중 하나만 올리는 것은 금지. **반드시 세트로** 처리한다.
   → **반드시 `/mnt/user-data/outputs/`에도 해당 `.md` 파일을 출력**하여, 사용자가 로컬에 다운로드 후 다음 대화에서 Claude에 업로드할 수 있도록 한다.
   → 출력 파일명 규칙: `{번호}_{파일명}.md` (예: `7.4_log_edoc.md`)
6. 코드 수정 시 **새로운 기능·규칙 추가 또는 오류 수정이 발생하면 무조건 관련 md 파일을 개정**한다.
   → 코드만 바꾸고 문서를 그대로 두는 것은 금지.
   → 해당 수정 사항과 관련된 **모든 md 파일을 빠짐없이 개정**한다 (직접 연관 + 간접 연관 파일 모두 포함).
7. md 파일 개정 시 **200줄을 초과할 경우 `a, b, c …` 접미사를 붙여 분할**한다.
   → 예: `2.2_hr_labor_annual.md` → `2.2a_hr_labor_annual.md` + `2.2b_hr_labor_annual.md`
   → 분할 시 `INDEX.md`도 함께 갱신하여 파일 목록에 반영한다.
   → 내용이 얇은 주제는 억지로 분할하지 말고 관련 파일로 병합하여 분절 방지.
8. 기존 배포된 코드를 수정할 때는 **반드시 서버(GitHub)의 코드를 로컬로 불러와 검토한 후 수정**한다.
   → 로컬 사본이나 기억에 의존하여 수정하는 것은 금지.
   → GitHub Contents API GET으로 최신 파일을 내려받은 뒤 작업 시작.
9. md 파일을 개정할 때는 **파일명 뒤에 rev 번호를 부여**한다.
   → 형식: `{번호}_{파일명}_r{n}.md` (예: `7.4_log_edoc_r2.md`, `2.2_hr_labor_annual_r3.md`)
   → 최신 rev 파일이 현행 기준 문서이며, 이전 rev는 이력으로 보존.
   → GitHub `docs/`와 `outputs/` 모두 rev 번호가 붙은 파일명으로 저장.

---

## 테스트 방식 정의

> Ground Rule 2번의 세부 절차. 모든 신규·수정 코드는 아래 순서를 반드시 준수한다.

### 1단계 — Unit Test
- **대상**: 개별 함수·메서드 등 가장 작은 단위의 코드
- **목적**: 각 단위가 의도대로 작동하는지 독립적으로 검증
- **통과 기준**: 모든 입력 케이스에서 예상 출력값 일치

### 2단계 — Integration Test
- **대상**: Unit Test를 통과한 모듈들을 결합한 상태
- **목적**: 모듈 간 interaction(호출·데이터 흐름·이벤트)에서 오류 없는지 검증
- **통과 기준**: 모듈 결합 후 사이드 이펙트·충돌 없음

### 3단계 — Acceptance Test
- **대상**: Integration Test를 통과한 코드를 기존 시스템에 편입한 상태
- **목적**: 전체 시스템과 충돌 없이 기능하는지 확인
- **방법**: 기존 코드를 GitHub에서 로컬로 내려받아 **mock-up(HTML format) test** 진행
- **필수 포함**: mock-up test는 반드시 **demonstration(실제 동작 시연)을 포함**해야 함
- **통과 기준**: demonstration까지 오류 없이 완료, 사용자 보고 후 승인

### 4단계 — 배포
- 위 3단계(Unit → Integration → Acceptance + Demonstration) **모두 통과한 경우에만** 배포 진행
- 단계 중 하나라도 실패 시 해당 단계부터 재시작

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
- **중첩 백틱 금지**: `innerHTML = \`...\`` 등 외부 template literal 내부에서 다시 백틱 사용 절대 금지
  → 브라우저가 내부 백틱을 template literal 종료로 오인하여 HTML 파싱 전체가 깨짐
  → 조건부 텍스트 생성 시 반드시 **문자열 연결(`+`)** 방식 사용
  ```js
  // ❌ 금지
  innerHTML = `...${condition ? `inner template` : ''}...`
  // ✅ 올바른 방식
  innerHTML = `...${condition ? 'text' + variable + 'text' : ''}...`
  ```
- **코드 섹션 교체 시 공유 함수 보존**: 한 섹션 내에 여러 기능이 공유하는 함수(예: `calcWorkDays`, `KR_HOLIDAYS`)가 있을 수 있음. 섹션 교체 시 해당 범위에 포함된 공유 함수가 새 코드에도 존재하는지 반드시 확인

---

## 배포 안전 규칙 (Roll-back)

> 배포 전·후 코드 무결성을 보장하기 위한 캐시 & 롤백 절차.

### 1. 배포 전 캐시 저장
- 배포 직전, **현재 GitHub에서 운영 중인 전체 코드를 로컬(`/home/claude/rollback/`)에 캐시**로 저장한다.
- 파일명 규칙: `{파일명}_backup_{yyyymmdd_HHMM}.html` (예: `portal_index_backup_20260626_1430.html`)
- 캐시 없이 배포하는 것은 금지.

### 2. 롤백 판단 기준
배포 후 아래 중 하나라도 해당하면 즉시 롤백을 검토한다:
- 기존에 정상 작동하던 기능이 깨지거나 오류 발생
- 신규 코드가 기존 모듈과 충돌
- 불필요한 업데이트로 판단되는 경우 (사용자 지시 포함)

### 3. 롤백 절차
```
① 캐시(/home/claude/rollback/)에서 직전 백업 파일 확인
② 백업 파일을 GitHub Contents API PUT으로 재업로드
③ 신규 배포 커밋을 덮어쓰는 방식으로 복원
④ 롤백 완료 후 사용자에게 보고
```
- 롤백 후 해당 이슈를 개발 로그(7.x.md)에 반드시 기록한다.

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
| **workers 마스터** | workers 컬렉션이 인사 정보의 원천. portal_users는 workers에서 읽어오는 방향 |
| **getWorkerData** | `window.getWorkerData(workerId)` — 계약서·전자결재에서 workers 데이터 로드용 전역 함수 |

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
