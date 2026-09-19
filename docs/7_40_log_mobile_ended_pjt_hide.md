# 모바일 종료 PJT(FAB/SUP) 노출 수정 (2026-09-19)

> 작성: 춘식이(Claude)

## 요청
대표님 — P4 Ph4 (SUP) 현장을 종료 처리해서 PC에서는 조회가 안 되는데 모바일에는 그대로 나옴. 모바일은 '현재 진행 중인' 일상 업무를 강조하는 방향으로 구축 예정. 카드 순서는 상관 없고 신규/종료 PJT만 제대로 나오면 됨.

## 원인
PC `index.html`은 `syncPjtSubtabsFromSettings()`에서 `pjt_settings/{p4ph2|p4ph4}.status==='ended'`이면 고정 PJT를 사이드바에서 제거한다. 모바일은 FAB/SUP가 고정 하드코딩(`m/home.html` 카드, `m/pjt.html` `SITES`, `m/schedule.html`의 `supSched`)이라 종료 상태를 전혀 읽지 않았다. 경량PJT는 `pjt_registry.status!=='ended'` 필터가 이미 있어 정상.

## 수정
1. `m/home.html` — FAB/SUP 카드에 id 부여, `pjt_settings` 두 문서 `onSnapshot`으로 종료 카드 숨김. 오늘 일정 배지 집계(`updateTodayBadge`)에서도 종료 PJT 제외. 확인 전 `visibility:hidden`(깜빡임 방지), 오류/3초 경과 시 노출.
2. `m/pjt.html` — `FIXED_KEY`/`fixedEnded`/`isEndedSite()` 추가. 홈 카드 필터, `SITE()`가 종료 시 `null`, `?site=` 딥링크 가드, 첫 렌더는 상태 확인 후(`fixedLoaded`, 2.5초 타임아웃), 이후 변경은 실시간 렌더.
3. `m/schedule.html` — 종료된 고정 PJT 일정 제외, 첫 렌더는 상태 확인 후.
4. 버전 주석: 모바일 홈 2.7.1 · 모바일 PJT 5.3.0 · 모바일 오늘 일정 1.0.1 (build 20260919b).

## 검증
- `node --check`(모듈 3파일 × 2레포), CSS 중괄호 깊이 0 — 통과
- jsdom + Firebase 목 실행 테스트 22항목 통과 (두 레포 파일 각각): 종료 시 카드/집계/일정 제외, 재개 시 복원(실시간), 딥링크 `?site=sup` 종료 시 홈 전환, 진행 중이면 정상 진입, 열람 중 종료 시 홈 전환, 조회 오류 시 카드 노출, 경량PJT 신규(status 없음)/종료/재개 표시
- production ↔ portal-test 파일 diff = Firebase 설정 3줄만 다름, 설정 혼입 없음

## 배포
대표님 지시("큰 건 아니니까 둘 다 동시에 해") 따라 production + portal-test 동시 배포. portal-test에는 동일 변경을 diff 패치로 독립 적용(파일 통복사 아님). 백업 `backup/v2.7.1/m/home.html`, `backup/v5.3.0/m/pjt.html`, `backup/v1.0.1/m/schedule.html`(양쪽, 경로 충돌 없음 확인).

## 참고
- `m/pjt_manday.html`(월간 공수)은 PC와 동일하게 FAB/SUP 고정 표시 유지.
- PC에서 바꾼 PJT 이름·설명(`pjt_settings.name/client/content`)은 모바일 FAB/SUP 카드에 아직 미반영.
