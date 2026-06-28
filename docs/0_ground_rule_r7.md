# 0. Ground Rule & 용어 정의

> JH Solutions 업무 포털 — 개발·운영 기준 문서
> 최초 작성: 2026-06-26 · 최종 수정: 2026-06-29(r7) · 작성: 춘식이(Claude)

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
   → rev.된 파일명 형식: `{번호}_{파일명}_r{n}.md`
   → `/mnt/user-data/outputs/`에도 동일 파일 출력.

6. **rev.된 md 파일은 GitHub `docs/`에 업로드**한다.

7. **모든 md 파일은 200줄 이내**로 관리한다.
   → 200줄 초과 시 파일명 뒤에 `a, b, c…` 접미사로 분할.

8. 분할 시 **`INDEX.md`도 함께 갱신**.

9. 코딩 완료 + md 파일 rev. 업로드 완료 후, **portal 전체를 통합 스냅샷으로 백업**한다.
   → 백업은 사용자 의사와 관계없이 **무조건 진행**.
   → 백업 후 **ver. no.는 반드시 사용자에게 확인** 후 저장.
   → **파일별 개별 버전 관리 금지** — portal 전체를 단일 버전으로 관리.
   → 저장 위치: `GitHub backup/v{ver}/` 폴더 + 로컬 `/home/claude/rollback/v{ver}/`
   → 폴더 내 파일: `portal_index.html`, `hr_index.html`, `gihoek_index.html`,
     `edoc_index.html`, `pjt_index.html`, `pjt_ph4_index.html`

---

## 백업 버전 관리 원칙

- **파일별 버전 분리 금지**: `hr_index_backup_v1.0.2`, `portal_index_backup_v1.0.3` 등 파일별로 버전이 다른 구조는 다른 대화에서 작업 시 상호 덮어쓰기 발생
- **단일 버전 스냅샷**: 배포 시점의 portal 전체 파일을 하나의 버전 폴더에 저장
- **롤백 시**: `backup/v{ver}/` 폴더의 모든 파일을 각 경로에 복원

```
backup/
  v1.0.3/
    portal_index.html   ← index.html
    hr_index.html       ← hr/index.html
    gihoek_index.html   ← gihoek/index.html
    edoc_index.html     ← edoc/index.html
    pjt_index.html      ← pjt/index.html
    pjt_ph4_index.html  ← pjt_ph4/index.html
```

---

## 테스트 방식 정의

### 1단계 — Unit Test
- 개별 함수·메서드 단위 독립 검증

### 2단계 — Integration Test
- 모듈 결합 후 interaction·데이터 흐름 검증

### 3단계 — Acceptance Test
- 전체 시스템 편입 후 mock-up HTML demonstration 포함 검증

### 4단계 — 배포
- 3단계 모두 통과 + 사용자 보고 후 승인 시에만 배포

---

## 기술 원칙

- **배포 전 항상 최신 SHA 확인**: PUT 전 반드시 GET으로 fresh SHA 조회
- **JS 문법 검증**: 배포 전 `node --check` 필수
- **window 전역 등록**: `<script type="module">` 내 onclick 대상 함수는 `window.fn` 등록 필수
- **실시간 동기화**: Firestore `onSnapshot` (localStorage 사용 금지)
- **탭 방식 확장**: 별도 페이지 생성 없이 탭으로 기능 추가

---

## 배포 안전 규칙 (Roll-back)

롤백 판단 기준: 기존 기능 파손 / 모듈 충돌 / 불필요한 업데이트

롤백 절차:
```
① backup/v{ver}/ 에서 직전 버전 파일 확인
② 각 파일을 GitHub Contents API PUT으로 원래 경로에 복원
③ 롤백 완료 후 사용자 보고
④ 해당 이슈를 개발 로그에 기록
```

---

## 용어 정의

| 용어 | 정의 |
|------|------|
| **포털** | `portal/index.html` — 로그인·계정관리·메뉴 분기 허브 |
| **앱** | 포털 내 각 업무 영역 (기획·인사·전자결재·PJT 등) |
| **via=portal** | 포털 경유 접근 파라미터 (`?via=portal`) |
| **Secondary App** | Firebase 2차 인스턴스 (관리자 세션 유지하며 타 계정 조작) |
| **_pw** | `btoa(encodeURIComponent(pw))` 형태로 저장된 비밀번호 |
| **perms** | 앱별 접근 권한 플래그 (`plan·hr·edoc·pjt`) |
| **posted** | 게시 완료 (전자결재) |
| **FAB** | P4 Ph2 — 귀뚜라미 범양냉방 FAB 현장 |
| **SUP** | P4 Ph4 — 귀뚜라미 범양냉방 SUP 현장 |
| **portalUid** | workers 컬렉션에서 portal_users를 연결하는 키 필드 |
