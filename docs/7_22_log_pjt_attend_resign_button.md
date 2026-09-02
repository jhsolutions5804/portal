# 7.22. 개발로그 — PJT 근태 화면 명단 관리 패널에서도 퇴사처리 가능하도록 추가

> 작성: 춘식이(Claude) · 2026-08-18

---

## 요청

직전 세션에서 근로자 마스터 관리(`pjt_manday/index.html`)에만 퇴사처리를 추가했는데, 대표님이 PJT 근태 화면(`pjt/index.html`)의 "명단 관리" 패널에서도 퇴사처리를 하려다 버튼이 없어서 못 함. 이 화면에서도 가능하게 해달라는 요청.

## 수정

- `pjt/index.html`, `pjt_ph4/index.html` 두 화면의 "명단 관리" 패널(`renderWorkerMgmtList`)에 각 인원별 **퇴사처리/재직전환** 버튼 추가
- `toggleWorkerResignFromUI(wid, currentlyResigned)`: `master_workers/{wid}` 문서에 `resigned`/`resignedDate` 직접 반영. 이 PJT의 `pjt_workers_fab`(또는 `pjt_workers_ph4`) 문서는 건드리지 않음 — 마스터 명부와 PJT별 명단이 서로 다른 컬렉션이기 때문에, 인원 추가 시 doc id를 마스터 id와 동일하게 맞춰 쓰던 기존 설계를 그대로 활용
- 팀장으로 지정된 인원은 퇴사처리 차단(마스터 명부 화면과 동일 규칙)
- 재직상태를 표시하기 위해 패널을 열 때 `master_workers` 전체를 한 번 조회해 캐시(`_masterResignedMap`)에 저장 (`loadMasterResignedMap`)
- **`pjt_ph4/index.html`(SUP)는 이번에 처음으로 명단 관리 패널에 이름/생년월일 인라인 수정 기능도 함께 이식**(기존엔 FAB에만 있었음, 8/18 오전 세션에서 SUP 반영이 누락되어 있었음). 텍스트 마스킹 방식 생년월일 입력도 동일 적용

## 실수 및 정정

- `pjt/index.html` 배포 시, 로컬 작업 사본이 이전 세션에서 버전코멘트만 프로덕션에 직접 반영(4.10.5)했던 시점 이후로 갱신되지 않은 상태였고, 이번 배포에서 그 로컬 사본을 그대로 올리면서 버전코멘트가 4.10.4로 되돌아가는 실수가 있었음(코드 내용 자체는 정상). 별도 커밋으로 4.10.6으로 정정.
- 재발 방지: 버전코멘트만 별도로 프로덕션에 직접 반영한 경우, 다음 세션에서는 반드시 프로덕션을 새로 clone/fetch한 뒤 이어서 작업할 것.

## 검증

- `node --check`로 `pjt/index.html`, `pjt_ph4/index.html`의 인라인 `<script>`/`<script type="module">` 블록 문법 검증 통과
- 함수 중복 선언 여부 grep으로 확인 (중복 없음)

## 배포

- `pjt/index.html`(4.10.4→4.10.6), `pjt_ph4/index.html`(신규: 명단관리 패널 전면 개선)
- 루트 `index.html` 버전배너 갱신 (build 20260818d, PJT 5.3.3)
- 백업: `backup/v5.3.14/{pjt,pjt_ph4}/index.html`
- 문서: `docs/4_1_pjt_fab_attend_progress.md` 갱신
- 프로덕션 직접 배포

---

## 2026-09-03 핫픽스 — 전체 출역/일괄 공수 적용의 퇴사자 필터 누락

### 증상
- 김짜장님이 8/15 퇴사처리한 4명(김혁·미첼·민지환·정대웅)의 개인별 공수표에 퇴사일 이후(8/21, 24~27) 공수가 계속 남아있는 것을 발견해 보고
- "퇴사처리 버튼을 8/15에 눌렀는데 어떻게 그 이후에 공수가 찍히냐" — 소급 처리 가설이 아니라 실제 버그였음

### 원인
- 퇴사자 제외 로직(`resignedDate<=dateKey` → 제외)은 **개별 체크/입력 화면(`renderWorkerList`의 `_ws`)에만** 적용되어 있었음
- **"✓ 전체 출역 체크"(`toggleAllWorkers`) / "일괄 적용"(`setAllManday`) 두 함수는 필터를 거치지 않고 `getWorkers()`(마스터 전체 명단)를 직접 호출** — 화면엔 퇴사자가 안 보이지만, 일괄 버튼을 누르면 뒤에서 퇴사자까지 포함해서 저장됨
- FAB에서 8/23(v-bf927cc0) 근태 배지/KPI 카운트 버그를 고치면서도 이 일괄처리 경로는 놓쳤던 것으로 보임

### 수정
- 공통 헬퍼 `getActiveWorkersForDate(dateKey)` 신설 (퇴사자 제외 로직을 한 곳에 집중)
- `renderWorkerList` / `setAllManday` / `toggleAllWorkers` 3곳 모두 이 헬퍼로 통일 — 개별/일괄 어느 경로든 동일하게 필터링되도록 구조 정리
- **FAB(`pjt/index.html`), SUP(`pjt_ph4/index.html`) 동일 적용**
- 확인 결과 경량PJT(`pjt_light`)는 일괄 버튼 자체가 없어 해당 버그 없음. 모바일(`m/pjt.html`)은 애초에 `master_workers`/`resignedDate` 체계를 안 씀 (별도 확인 필요 — 대기열에 추후 등록 검토)

### 소급 데이터 정리
- 코드 수정은 향후 재발만 막을 뿐, 이미 저장된 오염 데이터는 그대로 남음
- Firestore 직접 쓰기 네트워크 경로가 없어 브라우저 콘솔 스크립트(`cleanup_script.js`, dry-run → `applyCleanup()` 2단계 확인 방식)를 제작해 김짜장님께 전달 — 4명의 퇴사일 다음날부터 오늘까지 `worker_manday`를 순회해 본인 몫만 `deleteField()`로 제거
- 최초 실행 시 포털 홈(최상위 프레임)에서 콘솔을 열어 `window._fbDb`가 없다는 오류 발생 — 포털이 각 모듈을 iframe으로 로드하는 구조라 발생한 문제로, `pjt/index.html`을 직접 열거나 콘솔 프레임을 iframe으로 전환하도록 안내

### 검증
- `node --check`로 두 파일 모듈 스크립트 문법 검증 통과
- div 태그 열림/닫힘 개수 일치 확인
- `getActiveWorkersForDate`/`setAllManday`/`toggleAllWorkers` 중복 정의 없음, 구버전 `getWorkers().filter(...)` 잔존 없음 확인

### 배포
- 김짜장님 지시로 테스트 단계 생략, 프로덕션 직접 배포
- `pjt/index.html`: ver 4.10.7 → 4.10.8 (build 20260903)
- `pjt_ph4/index.html`: 버전 코멘트 관례 없음 (미갱신)
- 백업: `backup/v6.0.1/{pjt,pjt_ph4}/index.html`
- 문서: `docs/4_1_pjt_fab_attend_progress.md`, `docs/4_2_pjt_sup.md` 갱신
