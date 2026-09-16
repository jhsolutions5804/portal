# 7.34. 전자결재 — 결재 처리 후 결재요청(결재함) 복귀 수정

> 날짜: 2026-09-16 · 작성: 춘식이(Claude)

## 문제

전자결재 홈 → 결재 요청(9건) → 아무 문서(연차신청서, 업무일지 등)를 열어 승인/반려/게시 처리하면, 결재자가 원래 있던 결재요청(결재함) 화면이 아니라 **그 문서의 종류별 목록**(예: 연차신청서 → 연차신청서 목록, 업무일지 → 업무일지 목록)으로 이동해버리는 문제가 있었음.

## 원인

- `docApprove(docId, dtype, newStatus, docData)` — 연차/구매의서/지출결의서/초과근로 등 공통 결재 처리 함수. 처리 완료 후 항상 `renderDocList(dtype)`를 호출해 문서종류 목록으로 이동.
- `dailyApprove(docId, newStatus)` — 업무일지 전용 결재 처리 함수. 처리 완료 후 항상 `renderDailyList()`를 호출해 업무일지 목록으로 이동.
- 두 함수 모두 `openDocFromHome()`이 진입 시 세팅해두는 `_detailBackFn`(= `() => goTab('approve')`)을 참고하지 않고, 무조건 자기 문서종류 목록으로 하드코딩되어 있었음.

## 수정

`docApprove`, `dailyApprove` 두 함수의 처리 완료 분기 마지막을 아래와 같이 통일:

```js
// 승인/반려/게시 처리 후에는 문서종류 목록이 아니라 결재요청(결재함) 화면으로 돌아갑니다.
_detailBackFn = null;
if (typeof goTab === 'function') goTab('approve'); else renderDocList(dtype); // (dailyApprove는 renderDailyList())
```

진입 경로와 무관하게 항상 결재함(결재 요청) 탭으로 복귀하도록 통일. 목록 화면에서 직접 문서를 열람 후 뒤로가기(`목록으로`/`‹ 목록` 버튼)하는 기존 동작은 변경 없음 — 이번 수정은 오직 승인/반려/게시 "처리" 이후의 복귀 지점만 바꾼 것.

## 검증

- `docApprove`, `dailyApprove` 두 함수의 문자열 치환이 정확히 1회씩만 매칭되는지 확인 후 적용.
- `<script type="module">` 블록 추출 → import 구문 제거 → `node --check`로 문법 검증 통과 (production, portal-test 양쪽 파일 모두).
- production/portal-test 파일에 서로의 Firebase 설정이 섞이지 않았는지 `assert 'portal-test' not in content_prod` 확인.

## 배포

대표님 지시("동시에 배포해")에 따라 production + portal-test 양쪽 `edoc/index.html` 동시 배포.

- 버전: `ver 4.1.0` → `ver 4.1.1` (build 20260830a → 20260916a)
- 백업: `backup/v4.1.1/edoc/index.html` (양쪽 저장소)
- Pages 강제 재빌드 후 양쪽 `built` 상태 확인 완료

## 관련 문서

- `docs/3_1_edoc_daily_leave.md` (r3 갱신)
