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
