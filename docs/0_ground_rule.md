# 0. Ground Rule & 용어 정의

> JH Solutions 업무 포털 — 개발·운영 기준 문서
> 최초 작성: 2026-06-26 · 작성: 춘식이(Claude)

---

## 개발 GROUND RULE (필수 준수)

1. 사용자가 지시하는 **모든 작업은 대기열에 등록**한다.

2. 코드를 수정할 때는 **GitHub에 업로드된 가장 최신 ver.을 local로 가져와 edit**한다.
   → 기억·로컬 사본에 의존하는 것은 금지.
   → GitHub Contents API GET으로 최신 파일 내려받은 뒤 작업 시작.

3. 대기열에 있는 과제는 **local에서 test**를 진행한다.
   → test 방식은 하단 '테스트 방식 정의' 섹션을 따른다.

4. test 결과 이상이 없다면 **사용자 확인 후 배포**한다.
   → 보고 없이 임의 배포 금지.

5. 배포할 때마다 **기능 문서(1.x~6.md)와 개발 로그(7.x.md) 모두 rev. 진행**한다.
   → 기능 문서: 변경된 스펙·동작·UI·스키마 반영.
   → 개발 로그: 커밋 SHA·날짜·변경 내용·이슈 & 해결 기록.
   → 둘 중 하나만 rev.하는 것은 금지. 반드시 세트로 처리.
   → rev.된 파일명 형식: `{번호}_{파일명}_r{n}.md` (예: `7.4_log_edoc_r2.md`)
   → `/mnt/user-data/outputs/`에도 동일 파일 출력 (사용자 로컬 다운로드 → 다음 세션 업로드용).

6. **rev.된 md 파일은 GitHub `docs/`에 업로드**한다.
   → 최신 rev. 파일이 현행 기준 문서.
   → 이전 rev. 파일은 log 목적으로만 보존하며 운영 기준에서 제외.

7. **모든 md 파일은 200줄 이내**로 관리한다.
   → 200줄 초과 시 파일명 가장 뒤에 `a, b, c …` alphabet을 붙여 분할.
   → 예: `2.2_hr_labor_annual_r3.md` → `2.2_hr_labor_annual_r3a.md` + `2.2_hr_labor_annual_r3b.md`

8. 분할 시 **`INDEX.md`도 함께 갱신**하여 GitHub에 최신본 관리.

9. 코딩 완료 + md 파일 rev. 업로드 완료 후, **그 시점의 전체 코드를 백업**한다.
   → 백업은 사용자 의사와 관계없이 **무조건 진행**.
   → 백업 후 **ver. no.만 사용자에게 확인**한다.
   → 백업 파일은 **GitHub `backup/` 폴더와 local(`/home/claude/rollback/`) 양쪽에 동시 저장**.
   → 파일명 규칙: `{파일명}_backup_v{ver}_{yyyymmdd}.html` (예: `portal_index_backup_v1.2_20260627.html`)

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

## 배포 안전 규칙 (Roll-back)

> 배포 전·후 코드 무결성을 보장하기 위한 백업 & 롤백 절차.

### 1. 백업 (자동 — 무조건 진행)
- 코딩 완료 + md 파일 rev. 업로드 완료 시점에 **전체 코드를 자동 백업**한다.
- 사용자 의사와 관계없이 진행하며, **백업 후 ver. no.만 사용자에게 확인**한다.
- 저장 위치: **GitHub `backup/` 폴더** + **local `/home/claude/rollback/`** 동시 저장.
- 파일명 규칙: `{파일명}_backup_v{ver}_{yyyymmdd}.html`
  (예: `portal_index_backup_v1.2_20260627.html`)

### 2. 롤백 판단 기준
배포 후 아래 중 하나라도 해당하면 즉시 롤백 진행:
- 기존에 정상 작동하던 기능이 깨지거나 오류 발생
- 신규 코드가 기존 모듈과 충돌
- 불필요한 업데이트로 판단되는 경우 (사용자 지시 포함)

### 3. 롤백 절차
```
① local /home/claude/rollback/ 또는 GitHub backup/ 에서 직전 백업 파일 확인
② 백업 파일을 GitHub Contents API PUT으로 재업로드 (덮어쓰기 복원)
③ 롤백 완료 후 사용자에게 보고
④ 해당 이슈를 개발 로그(7.x.md)에 기록
```

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
