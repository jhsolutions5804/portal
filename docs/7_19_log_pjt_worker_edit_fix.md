# 7.19. 개발로그 — PJT 기술인 명단 이름/생년월일 수정 기능 추가

> 작성: 춘식이(Claude) · 2026-08-18

---

## 문제

`pjt/index.html`의 "기술인 출역 현황 → ⚙️ 명단 관리" 패널에서:

1. 생년월일이 비어있는 인원만 최초 1회 입력 가능(`<input type="date">`). 이미 입력된 인원의 생년월일과, 모든 인원의 이름은 수정할 방법이 UI에 아예 없었음.
2. 생년월일 입력 시 네이티브 `<input type="date">`의 day 세그먼트에 "1"을 입력하고 "0"을 이어 입력하기 전에 짧게 멈추면, 브라우저가 자동으로 "01"로 확정하고 포커스를 month 세그먼트로 넘겨버려 "10일"을 의도해도 "01일"로 저장되는 문제.

## 원인

- `renderWorkerMgmtList()`가 `w.birth` 존재 여부로 분기: 있으면 static `<span>`, 없으면 1회용 `<input type="date">` → 수정 진입점 자체가 없었음.
- 이름은 애초에 항상 static text로만 렌더링.
- 생년월일 입력은 네이티브 date 위젯의 세그먼트 자동확정 동작(브라우저 표준 동작)에 그대로 노출되어 있었음.

## 수정

- `renderWorkerMgmtList()`에 인라인 수정 모드 추가: 인원당 "수정" 버튼 → 이름(text input) + 생년월일(text input, YYYY-MM-DD 마스킹) 편집 → "저장"/"취소"
- `_maskBirthInput(el)`: 숫자만 추출 후 4자리/6자리 지점에 자동으로 하이픈 삽입. 네이티브 date input을 쓰지 않으므로 세그먼트 자동확정 문제가 발생하지 않음
- `saveWorkerEditFromUI(wid)`: 이름 필수, 생년월일 형식(`/^\d{4}-\d{2}-\d{2}$/`) 검증 후 저장
- Firebase: `window._fbUpdateWorker(workerId, {name, birth})` 신규 추가 (`setDoc(..., {merge:true})`) — 기존 `_fbUpdateWorkerBirth`는 하위호환용으로 유지
- 기존 "생년월일 미입력 인원만 인라인 입력" 로직은 제거하고, 수정 모드로 통합

## 검증

- `node --check`로 인라인 `<script>` / `<script type="module">` 블록 문법 검증 통과
- 프로덕션 파일과 diff하여 의도한 변경 외 부작용 없음 확인

## 배포

- `pjt/index.html`: build `20260818` · ver `4.10.4`
- 루트 `index.html` 버전배너: PJT `5.3.0` → `5.3.1`
- 백업: `backup/v5.3.1/pjt/index.html` (변경 전 스냅샷)
- 문서: `docs/4_1_pjt_fab_attend_progress.md` 갱신
- 프로덕션 직접 배포 (대표님 확인 후 진행)
