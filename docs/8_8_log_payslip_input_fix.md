# 8_8 · 급여명세서 상여금/특별상여/기타수당 입력 커서 초기화 버그 수정 (r5)

**작업일**: 2026-07-22
**대상**: `hr/index.html`
**요청 계기**: 대표님 — "급여명세서에서 상여금, 특별상여, 기타수당 입력할 때 한 글자씩 입력해야 하는 번거로움이 있네." (스크린샷 첨부)

## 배경 (경위)
- 첨부 스크린샷은 PC 급여명세서 작성 화면(`renderPayslipPCRight`)의 지급/공제 내역 카드
- 코드 검색 결과 해당 3개 필드가 공유하는 `inp()` 헬퍼 함수가 `oninput` 이벤트로 매 키 입력마다 우패널 전체를 `innerHTML`로 재생성하고 있었음 → input DOM 교체로 포커스/커서 소실 → 매 글자마다 재클릭 필요

## 원인
```js
const inp = (id, val, ph='0') =>
  `<input type="number" id="${id}" value="${val||''}" placeholder="${ph}"
    oninput="ps.${id.replace('ps-','')}=this.value;renderPayslipPCRight()"
    ...>`;
```
같은 화면의 기본급·4대보험·기숙사 입력란은 이미 `onchange`(포커스 이탈 시에만 반영)를 사용해 문제가 없었음. 기존 문서(`docs/2_5_hr_payslip_r3.md`)에도 "기숙사 공제: onchange 사용 (oninput 사용 시 오류)"라는 주의사항이 이미 있었는데, `inp()` 헬퍼(상여금/특별상여/기타수당)에는 이 원칙이 누락되어 있었던 것.

## 수정 내용
- `inp()` 헬퍼의 `oninput` → `onchange`로 변경 (파일 내 정확히 1줄 diff)
- 타이핑 중에는 재렌더링 없이 자유롭게 입력 가능, 필드 이탈 시 지급계/공제계/실지급액 갱신 (기존 다른 필드와 동일 동작 방식으로 통일)

## 검증
- `diff`로 변경 범위가 의도한 1줄인지 확인
- 전체 `<script>` 5개 블록 `node --check` 문법 검증 통과

## 배포
- 대표님이 **portal-test 생략, 프로덕션 직접 배포** 선택 → 바로 production 배포
- production 커밋: `hr/index.html` `9ad3f5d`, `index.html`(버전주석) `a8a300f`
- 버전 주석(`index.html`): build 20260722, ver 2026-07-22 (hr payslip **2.6.2** 추가), "급여명세서 상여금/특별상여/기타수당 입력 시 한글자마다 커서 초기화되는 버그 수정(oninput→onchange)" 반영
- 백업: `backup/v2.6.2/hr_index_20260722.html` `7cf9652`
- 문서 갱신: `docs/2_5_hr_payslip_r3.md`(r5 내용 추가), `docs/7_3_log_hr_r10b.md`

## 참고
- 모바일 작성 폼(`renderPayslipWriteForm`)은 이미 `onchange` 사용 중이라 이번 버그 해당 없음
