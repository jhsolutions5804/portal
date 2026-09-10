# 7.33 개발로그 — 공수 집계표 모달, 퇴사자 제외 필터 누락분 수정

- **날짜**: 2026-09-10
- **계기**: 대표님 — 공수 집계표 스크린샷 공유하며 "퇴사한 애들은 왜 뜨는 거야" (민지환 — 퇴사자, 9월 탭에 0일/0.0공수로 계속 노출)
- **대상 파일**: `pjt/index.html` (FAB)

## 원인
4.10.8(2026-09-03) 핫픽스에서 근태관리의 개별 체크(`renderWorkerList`) / 일괄 체크(`toggleAllWorkers`) / 일괄 공수(`setAllManday`) 세 곳을 공통 헬퍼 `getActiveWorkersForDate(dateKey)`로 통일했으나, **"📋 이달 공수 집계표 보기" 모달(`openKongsuModal`/`renderKongsuTabs`/`renderKongsuSheet`)은 이 작업에서 빠져 있었음** — 여전히 `getWorkers()`(전체 명부, 퇴사 필터 없음)를 직접 참조하고 있어 퇴사자가 탭에 계속 노출됨.

## 수정
- `_ksDateKey()` 헬퍼 추가: 조회 중인 달(`_sheetY`/`_sheetM`)의 **말일** 기준 dateKey 생성.
- `openKongsuModal`/`renderKongsuTabs`/`renderKongsuSheet` 세 곳 모두 `getWorkers()` → `getActiveWorkersForDate(_ksDateKey())`로 교체.
- `openKongsuModal`에 `await loadMasterResignedMap()` 추가(재직상태 캐시 최신화 보장).
- `changeSheetMonth`(월 이동)에도 `renderKongsuTabs()` 호출 추가 — 기존엔 월 이동 시 시트만 갱신되고 탭 목록은 갱신 안 되던 부수 개선.

## portal-test 이식 시 주의사항
- portal-test는 4.10.8 통일 리팩터링 자체가 아직 반영 안 된 상태라 **`getActiveWorkersForDate` 함수가 존재하지 않음**(각 화면마다 `_masterResignedMap` 인라인 필터가 개별적으로 남아있는 구버전 구조).
- 없는 함수를 호출하면 `ReferenceError`가 나므로, production과 동일한 이름의 함수를 억지로 맞추지 않고 **portal-test 전용 인라인 헬퍼 `_ksActiveWorkers()`**(기존 `_masterResignedMap` 캐시 재사용)를 새로 작성해 동일 로직만 이식. 코드가 100% 동일하지 않음에 유의 — 추후 portal-test에도 `getActiveWorkersForDate` 공통 리팩터링을 별도로 진행할 필요 있음.

## 검증
- `node --check`로 production/test 양쪽 script 전체 문법 검증 통과.

## 배포
- production + portal-test 양쪽 `pjt/index.html` 배포. 대표님 "테섭 본섭 모두 배포" 지시로 동시 진행.
- 버전: production `4.10.8 → 4.10.9`, portal-test `4.10.7 → 4.10.8(test)`.
- 백업: `backup/v6.0.2/pjt/index.html`(production), `backup/v1.0.3/pjt/index.html`(portal-test).

## 관련 문서
- `docs/4_1_pjt_fab_attend_progress.md` §퇴사자 제외 필터 통일 절에 후속 항목 추가
