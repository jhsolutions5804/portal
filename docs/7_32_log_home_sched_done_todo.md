# 7.32 개발로그 — 포털 홈 일정관리 완료체크 + 할 일(할일) 옵션 추가

- **날짜**: 2026-09-10
- **요청**: 대표님 — "PJT 홈 - 일정관리에서도 완료체크 할 수 있게 해주고, 일정 등록할 때 '할 일' 체크도 할 수 있게 해줘."
- **대상 파일**: `index.html` (포털 홈, root)

## 배경
`user_schedules`/`ph4_schedules` 스키마에는 이미 `isTodo` 필드가 존재했으나(문서 4.5.0 참조), 홈 일정 등록 폼(`saveHomeSched`)에서는 항상 `isTodo:false`로 하드코딩 저장되고 있었고, UI에도 관련 토글이 없었음. 완료체크(`done` 필드)도 PJT 앱(`pjt/index.html`)에는 있었지만 홈 캘린더 상세 목록에는 없었음.

## 수정 내용
1. **할 일 토글**: 등록/수정 폼에 "할 일 (시간 없이 체크리스트로 등록)" 토글(`_hscSetTodo`/`toggleHscTodo`) 추가. 켜면 시작/종료 시간 입력 블록(`hsc-time-block`)이 비활성화되고, 저장 시 `isTodo:true` + `stime`/`etime` 공란 처리. 기존 pjt/index.html의 `usf-todo-wrap` 패턴을 그대로 이식.
2. **완료체크**: 우측 상세 패널의 일정 목록(`pjtCalSelectDay`) 각 항목 앞에 체크박스(`hsc-check`) 추가. 클릭 시 `toggleHomeSchedDone(idx, el)`가 로컬 상태(`_homeSchedItems`, `_pjtCalCache`)를 낙관적으로 갱신하고 `_hscSetDone`이 Firestore 문서에 `done`/`doneUpdatedAt` 필드로 저장(PJT 앱 `_usSetDone`과 동일 패턴). 완료 시 취소선.
3. `isTodo:true` 항목은 목록에 "할일" 배지 표시.

## 검증
- `node --check`로 module script 전체 문법 검증 통과 (import 구문 제거 후 검사).
- CSS 중괄호 depth 검증 통과 (최종/최소 depth 0).

## 배포
- production(`portal`) + portal-test(`portal-test`) 양쪽 `index.html` 배포. 대표님 확인 후 "테섭 본섭 모두 배포" 지시로 동시 진행.
- 버전: production `portal home 1.0.3 → 1.0.4`, portal-test 동일 내용 반영.
- 백업: `backup/v6.0.2/index.html`(production), `backup/v1.0.3/index.html`(portal-test).

## 관련 문서
- `docs/4_0_pjt_home.md` §4.5.1 갱신
