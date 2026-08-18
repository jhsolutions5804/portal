# 7.21. 개발로그 — 근로자 마스터 명부 퇴사처리 기능 추가

> 작성: 춘식이(Claude) · 2026-08-18

---

## 요청

근로자 마스터 관리(`pjt_manday/index.html`)에서 인원 퇴사처리가 가능하게 해달라는 요청. 기존엔 "삭제"만 있어서, 퇴사한 사람을 완전히 지우면 과거 근태·공수 기록까지 없어질 위험이 있고, 그렇다고 그냥 두면 신규 PJT 투입 시 계속 선택 가능한 상태로 남는 문제가 있었음.

## 설계

- `master_workers/{id}`에 `resigned`(boolean), `resignedDate`(YYYY-MM-DD) 필드 추가. **삭제가 아닌 상태 플래그** 방식으로, 기존 PJT 투입 이력·근태·공수 기록에는 전혀 영향 없음.
- 퇴사자는 목록에 계속 표시(회색 취소선 + "퇴사 · 날짜" 배지)하되, 신규 투입 대상에서만 제외.

## 수정 내역

- `pjt_manday/index.html`
  - `renderMasterTable()`: 퇴사자 회색 취소선 표시, 배지 추가, 재직자 우선 정렬
  - `renderLeaderOptions()`: 퇴사자를 팀장 후보에서 제외
  - `toggleResign(id)` 신규: 퇴사처리(퇴사일 입력) / 재직 전환 토글. 팀장인 경우 퇴사처리 차단(삭제와 동일 규칙)
- `pjt/index.html`, `pjt_ph4/index.html`, `pjt_light/index.html`
  - 각 PJT의 "마스터 명부에서 선택" 신규 투입 드롭다운(`loadMasterOptions`/`openWorkerAdd`)에서 `m.resigned===true`인 인원 제외
  - 이미 해당 PJT에 투입되어 있던 사람은 영향 없음(제거하지 않음)

## 검증

- `node --check`로 4개 파일의 인라인 `<script>`/`<script type="module">` 블록 문법 검증 통과

## 배포

- `pjt_manday/index.html` (1.1.1→1.1.2), `pjt/index.html` (4.10.4→4.10.5), `pjt_ph4/index.html`(버전코멘트 없는 파일, 내용만 반영), `pjt_light/index.html` (3.1.0→3.1.1)
- 루트 `index.html` 버전배너 갱신 (build 20260818c)
- 백업: `backup/v5.3.13/{pjt_manday,pjt,pjt_ph4,pjt_light}/index.html`
- 문서: `docs/4_4_pjt_manday.md` 갱신
- 프로덕션 직접 배포
