# 8_8 · 초과근로 결재 목록 본인 작성분만 표시 (r1)

**작업일**: 2026-07-23
**대상**: `edoc/index.html`
**요청 계기**: 대표님 스크린샷 — "초과근로 탭에서 내 것 말고 다른 사람 것 안 보이게 해줘"

## 배경
- "초과근로 결재" 탭(`renderOvertimeMain`)이 `edoc_overtime` 컬렉션을 필터 없이 전체 조회 → 이한영·정다애 등 다른 직원이 상신한 건까지 로그인한 모든 사용자에게 노출되고 있었음

## 수정
```js
const myUid=(_user&&_user.uid)||'';
docs=docs.filter(d=>d.authorUid===myUid);
```
- `renderOvertimeMain()`에 본인 작성분(`authorUid` 일치) 필터 추가, admin 예외 없음
- 결재 처리는 별도 **결재함**(`renderApproveBox`) 탭에서 그대로 가능 — 영향 없음 확인

## 검증
- `node --check` (모듈 스크립트 `.mjs` 추출) 통과

## 배포
- 대표님 지시로 **테스트서버 생략, 본섭 직접 배포**
- 커밋: `edoc/index.html` `a6893b9`, `index.html`(버전주석) build 20260723
- 백업: `backup/v2.6.2/edoc/index.html`
- 문서: `docs/3_4_edoc_overtime_r1.md`(r3), `docs/7_4_log_edoc.md`
