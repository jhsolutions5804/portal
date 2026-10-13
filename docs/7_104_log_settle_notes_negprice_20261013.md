# 7.104. 개발로그 — 정산서 특이사항 · 마이너스(네고) 단가 (2026-10-13)

- 대표님 요청(2026-10-13): 정산서에도 견적서처럼 특이사항을 쓸 수 있게, 네고 가격을 넣어야 하니 마이너스 단가도 입력 가능하게 — 오늘 중 발행 필요(긴급).
- `gihoek/index.html`(20261013a): 정산서 작성 화면 `특이사항` 입력란(`d.notes` → 문서 `notes`), 상세·인쇄/PDF 표시, `fmtMoneyNeg`(직접 입력 단가·금액 전용 마이너스 허용), 안내문·placeholder, `inputmode=text`. 상세는 `1_4_gihoek_settle.md` 마지막 절.
- 영향 범위: `직접 입력` 방식과 모든 방식의 특이사항만. 합계 0 이하 발행 차단·부가세 계산·회계 반영(`supply`·`total`)은 그대로이며 다른 화면의 `fmtMoney`는 변경 없음.
- 백업 `backup/v_settle_notes_20261013/gihoek/index.html`(변경 후 사본, 되돌릴 때는 `git revert`).
