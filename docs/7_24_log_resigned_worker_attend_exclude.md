# 7.24. 개발로그 — 퇴사처리된 인원 퇴사일 이후 출역 체크리스트에서 자동 제외

> 작성: 춘식이(Claude) · 2026-08-18

---

## 문제

직전 세션에서 퇴사처리 기능을 추가했지만, `master_workers`의 `resigned` 플래그가 PJT 근태 화면의 일별 출역 체크리스트(`renderAttend`→`renderWorkerList`)에는 전혀 반영되지 않았음. 퇴사처리된 인원도 계속 체크리스트에 남아 출역 체크·공수 입력이 가능한 상태였음.

## 원인

`renderWorkerList()`가 `getWorkers()`(해당 PJT의 `pjt_workers_fab`/`pjt_workers_ph4` 문서)만 그대로 나열했고, `master_workers`의 재직상태를 조회하지 않았음. 명단 관리 패널(`renderWorkerMgmtList`)에만 `_masterResignedMap`을 로드해서 배지를 표시했을 뿐, 출역 체크리스트 쪽에는 이 데이터를 아예 가져오지 않고 있었음.

## 수정

- `renderAttend()` 시작 시 매번 `loadMasterResignedMap()`을 호출해 `_masterResignedMap`을 최신화하고, 완료되면 `renderWorkerList()`를 재호출
- `renderWorkerList()` 내부의 `_ws`(표시 대상 인원 목록) 계산에 필터 추가: `resigned===true`이고 `resignedDate <= dateKey`(조회 중인 날짜)인 인원은 제외
  - 날짜 문자열이 둘 다 `YYYY-MM-DD` 형식이라 문자열 비교만으로 날짜 선후 비교가 정확히 됨
  - **퇴사일 이전 과거 날짜**를 조회할 때는 그 시점엔 재직 중이었으므로 계속 표시 — 과거 근태 기록이 사라지지 않도록 함
  - "전체 N명" 인원수 표시에도 동일하게 반영
- `toggleWorkerResignFromUI()`에 `renderAttend()` 재호출 추가 — 명단 관리 패널에서 퇴사처리하면 출역 체크리스트도 그 자리에서 바로 갱신됨
- FAB(`pjt/index.html`)·SUP(`pjt_ph4/index.html`) 양쪽에 동일 적용

## 검증

- `node --check`로 두 파일의 인라인 `<script>` 블록 문법 검증 통과
- `loadMasterResignedMap`/`renderAttend`가 같은 `<script>` 블록(모듈 아님) 내에 위치해 함수 선언 호이스팅으로 정상 호출됨을 소스 위치로 확인

## 배포

- `pjt/index.html`(4.10.6→4.10.7), `pjt_ph4/index.html`
- 루트 `index.html` 버전배너 갱신 (build 20260818f, PJT 5.3.4)
- 백업: `backup/v5.3.16/{pjt,pjt_ph4}/index.html`
- 문서: `docs/4_1_pjt_fab_attend_progress.md` 갱신
- 프로덕션 직접 배포
