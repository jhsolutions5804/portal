# 7.35. 인사 — 근로자 명부 퇴직 처리/재직 복구 기능

> 날짜: 2026-09-16 · 작성: 춘식이(Claude)

## 요청

대표님 — "근로자 명부에 퇴직 기능 추가해줘."

## 배경

기존 근로자 명부(`hr/index.html`, `workers` 컬렉션)에는 `rosterDelete`(영구 삭제)만 있고, 계약서·급여명세서 등 연결 데이터를 유지한 채 "퇴직" 상태만 표시하는 방법이 없었음.

## 구현

- `workers/{id}`에 `status`('resigned' | 미설정=재직), `resignDate` 필드 추가.
- `rosterDetail` 상세 모달: 재직중(🟢)/퇴직(🔴 + 퇴직일) 배지, `🚪 퇴직 처리`/`↩️ 재직으로 복구` 버튼 추가.
- `rosterResign(id, name)`: `prompt()`로 퇴직일 입력 → 확인 후 즉시 `status:'resigned', resignDate` 저장 (별도 "수정 저장" 불필요).
- `rosterUnresign(id, name)`: 확인 후 `status:'active'`, `resignDate` 필드 삭제(`deleteField()`).
- `calcWorkDays(hireDate, resignDate)` — 퇴직자는 재직 기간/실 근무일수/퇴직금(예상) 계산의 종료일을 퇴직일로 고정(기존엔 항상 "오늘" 기준).
- `renderRosterList` 목록: 퇴직자 행 배경 흐리게 + 이름 옆 `퇴직` 배지, 정렬 시 최하단 배치. 삭제되지 않으므로 계속 조회 가능.

## 검증

- `docApprove`류 함수와 별개 파일이지만 동일 절차: 문자열 치환 정확히 1회 매칭 확인 → `<script type="module">` 추출 후 `node --check` 통과(production/portal-test 양쪽) → `assert 'portal-test' not in content_prod` 확인.

## 배포

대표님 지시("동시에 배포해")에 따라 production + portal-test `hr/index.html` 동시 배포.

- 버전: `ver 2.2.0` → `ver 2.3.0` (build 20260830b → 20260916a)
- 백업: `backup/v2.3.0/hr/index.html` (양쪽)
- Pages 강제 재빌드 후 양쪽 `built` 확인

## 관련 문서

- `docs/2_1_hr_roster_r5.md` (r6 갱신)

## 영향 범위 밖 (참고)

`퇴직금 정산`(`docs/2_6_hr_retire_r2.md`) 모듈은 기존처럼 퇴직일을 매번 수동 입력하는 별도 플로우 — 이번 `resignDate`와 자동 연동은 하지 않음. 필요 시 추후 연동 검토.
