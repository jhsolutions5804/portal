# 7.36. 인사 — 근로자 명부 중복 렌더함수 버그 수정 + 재직자/퇴사자 필터

> 날짜: 2026-09-16 · 작성: 춘식이(Claude)

## 요청

대표님 (스크린샷 2장 첨부):
1. "근로자 명부에서 퇴사자 따로 볼 수 있게 해주고."
2. "뭔가 수정하고 나면 근로자명부 화면이 이상하게 바뀌는데, 이거 고쳐주고. 첫 번째 첨부한 이미지로 항상 보여지면 좋겠네."

## 원인 진단 (문제 2)

`hr/index.html`에 `window.renderRosterMain`이 **두 번 정의**되어 있었음(2807줄대, 2929줄대) — JS는 뒤에 정의된 것으로 덮어쓰므로 실제로는 두 번째 정의만 동작. 근로자 명부 탭 진입(`goTab('roster')`)은 이 최신 정의를 호출해 정상 테이블(스크린샷 1번, 10열 + 신규등록 버튼)을 보여줌.

문제는 `rosterDetailSave`, `rosterDelete`, `rosterEmpNoSave`, `rosterLinkPortal`(그리고 이번 세션 초반에 추가한 `rosterResign`/`rosterUnresign`)이 전부 `renderRosterMain()`이 아니라 **완전히 별도로 존재하던 구버전 함수 `renderRosterList`**(6열짜리 카드형 레이아웃, 뒤로가기 버튼, 신규등록 버튼 없음 — 스크린샷 2번)를 호출해 화면을 갱신하고 있었음. 즉 명부 화면 자체가 아니라 "수정 후 갱신 시 호출하는 함수"가 잘못된 레거시 함수를 가리키고 있었던 것이 원인.

## 수정

1. 항상 덮어써지던 죽은 첫 번째 `renderRosterMain` 정의 삭제.
2. 더 이상 쓸모없어진 구버전 `renderRosterList` 함수 전체 삭제(6열 레이아웃, 뒤로가기 버튼 포함).
3. 모든 수정/삭제/퇴직처리 액션의 화면 갱신 호출(`renderRosterList();` × 6곳)을 `renderRosterMain();`으로 통일.
4. (부수적) 이번 참에 명부의 유일한 정식 렌더 경로가 하나로 좁혀졌으므로, 향후 유사한 "숨은 레거시 함수" 재발 가능성 차단.

## 추가 (요청 1)

`renderRosterMain` 상단에 **🟢 재직자 (N) / 🔴 퇴사자 (N)** 필터 탭 추가.

- `let _rosterViewFilter = 'active';` 모듈 전역 상태, `window.rosterSetFilter(f)`로 전환.
- 기본값은 재직자 탭 — 퇴사자가 쌓여도 평소 목록이 지저분해지지 않음.
- 퇴사자 탭 선택 시 이름 옆에 `퇴직 YYYY-MM-DD` 배지 표시.
- 탭 버튼에 각각 재직자/퇴사자 인원수 표시(로딩 완료 후 실제 데이터 기준으로 갱신).
- 지난 세션(v2.3.0)에서 추가한 상세 모달의 🚪 퇴직 처리 / ↩️ 재직으로 복구 버튼은 그대로 유지.

## 검증

- 문자열 치환 각 1회씩만 매칭되는지 assert로 확인.
- 삭제 후 `renderRosterList` 문자열이 파일에 전혀 남지 않았는지 확인.
- 남겨야 하는 `rosterEmpNoCancel`(구버전 정의에만 존재, 다른 곳에서 재정의되지 않음)은 삭제 대상에서 제외해 정상 보존.
- `<script type="module">` 추출 → `node --check` 통과(production/portal-test 양쪽).
- `assert 'portal-test' not in content_prod` 확인.

## 배포

대표님 지시("동시에 배포해" — 이전 세션 지시를 이번 수정에도 동일 적용) 따라 production + portal-test `hr/index.html` 동시 배포.

- 버전: `ver 2.3.0` → `ver 2.4.0` (build 20260916a → 20260916b)
- 백업: `backup/v2.4.0/hr/index.html` (양쪽)
- Pages 강제 재빌드 후 양쪽 `built` 확인

## 관련 문서

- `docs/2_1_hr_roster_r5.md` (r7 갱신)
