# 7.18. 기획 — 견적서 품목 비고란 추가 로그

> 작업일: 2026-08-13 · 작성: 춘식이(Claude)

---

## 요청

대표님 요청: 품목 목록에서 품명·규격 다음, 금액 옆에 비고란 추가.

## 구현

**데이터**: `gihoek_estimates/{id}.items[].remark` (string, 선택입력). 기존 견적의 items는 remark 필드가 없으므로 읽을 때 `''` 폴백.

**작성/수정 폼**:
- 헤더/colgroup에 "비고" 열 추가 (`#·품명·규격·수량·단가·금액·비고·삭제` 순서)
- `drawRows()`에 비고 입력 `<input>` 셀 추가, `setItem(i,'remark',this.value)`로 값 반영
- `newEst()`/`editEst()`/`addRow()`/`delRow()`의 기본 item 객체에 `remark:''` 추가

**저장 (`saveEst`)**: items map에 `remark:(i.remark||'').trim()` 추가

**상세보기 (`openEst`)**: 품목 표에 "비고" 컬럼 추가

**인쇄/PDF (`printEst`)**: 품목 표에 "비고" 컬럼 추가. tfoot(공급가액/부가세/합계금액) 행은 열 개수가 6→7로 늘어난 만큼 각 행 끝에 빈 `<td></td>` 추가해 정렬 유지.

## 검증

- `node --check` 문법 검증 통과
- 배포 전/후 diff로 의도한 변경 지점만 수정됐는지 확인 (29줄, 모두 remark 관련)

## 배포

- `gihoek/index.html` (build 20260813e)
- 루트 `index.html` 버전 코멘트: gihoek 5.3.9 → 5.3.10
- 백업: `backup/v5.3.11/gihoek/index.html`
- 기능문서: `docs/1_3_gihoek_estimate_r6.md` → `docs/1_3_gihoek_estimate_r7.md`
