# 7.107. 개발로그 — 급여명세서 마이너스 입력 · 지급/공제 항목 직접 추가 (2026-10-19)

- 대표님 요청(2026-10-19): 급여명세서에도 `-` 입력, 지급·공제 항목을 직접 추가/수정. 본섭 구포털 인사(`hr/index.html`, 2.28.0 build 20261019a).
- 변경: `fmtMoneyNeg` 신설(`hr/index.html` 모듈 스크립트), 금액 칸 14곳을 마이너스 허용 서식으로, `psWonR`/`psWon` 음수 표기와 `psDedWon`·`psEscH` 추가, `ps.customPay`/`ps.customDeduct` 상태·`psNormCustom`·`psCustomAdd/Del/Set`·`psRenderCustomItems`, `psCalcAll` 합계 반영, 저장(PC·모바일 `psSave` 둘 다)에 `customPay`·`customDeduct`, 저장값 복원 `__psSavedC`, 미리보기·현재 양식(v5)에 직접 추가 행. 상세는 `2_5_hr_payslip_r3.md` 마지막 절.
- 설계 결정(대표님께 확인 필요 시 변경 가능): 직접 추가 지급은 기본 **과세**(4대보험·소득세 산정 포함), `비과세` 체크 시 여비교통비와 같은 취급. 공제는 보험 산정과 무관. 기본 항목(기본근로수당·상여금 등)의 이름은 바꾸지 않고 금액만 기존처럼 수정 — 이름이 다른 항목은 직접 추가로 만든다.
- 영향: 직접 추가 항목이 없으면 계산·저장·양식 출력이 이전과 동일(시험). 명세서를 읽는 다른 화면(`m/hr.html` 조회·발송, `gihoek` 급여 직접비 분배의 `netPay`)은 저장된 합계를 그대로 쓰므로 변경 없음.
- 새 영업기획이 아닌 새 플랫폼 인사 모듈(`app/modules/hr/payslip*.js`, 양식 v7)에는 별도 구현이 필요 — 대조 이식 목록(`prod-sync-ledger`)에 기록.
- 백업 `backup/v_payslip_custom_20261019/`(변경 후 사본, 되돌릴 때는 `git revert`).
