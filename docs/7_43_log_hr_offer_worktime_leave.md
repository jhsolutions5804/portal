# 개발로그 — 인사: 연봉 제안서 별도지급 표시 + 근로시간 휴가 직접 부여

> 작성: 춘식이(Claude) · 2026-09-23

## 요청

1. 연봉제안서 출력할 때 계약연봉 외 급여명세서에 표시된 수당 항목(기술수당·여비교통비)도 보여주면 좋겠다.
2. 근로시간 메뉴에서 관리자 계정으로 휴가도 직접 부여할 수 있게 해달라.

## 구현

### 연봉 제안서 — 별도지급 표시 (v2.7.0)

- `_offerWorkers`에서 선택된 근로자의 `certifications`를 세어 급여명세서와 같은 `calcTechAllowance()`로 기술수당 실금액 계산, 출력 "별도 지급" 행에 `보유 자격증 N개 × 단가 = 월 OOO원` 형태로 표시.
- 근로자 미선택·자격증 0개면 일반 안내문(1개당 단가, 상한 없음)으로 대체 — 에러 없이 항상 표시됨.
- 여비교통비는 금액이 매일 달라 고정값을 못 매기므로 표준 요율표 텍스트로 안내(근로계약서 조항과 동일 기준).
- `renderOfferMain()` 진입 시 `loadTechAllowanceConfig()`를 백그라운드 호출해 단가를 미리 캐시(급여명세서 화면과 동일 패턴).
- 상세: `2_10_hr_offer.md`.

### 근로시간 — 관리자 휴가 직접 부여 (v2.7.0)

- 기존 "연차 현황" 탭의 `openLeaveAdminForm()`(관리자 연차 등록 모달)을 그대로 재사용 — 신규 컬렉션·계산 로직 없음.
- `preset` 파라미터 추가로 근로자명·날짜를 프리필하고, `dataset.returnJson`으로 "근로시간 탭에서 열렸다"는 복귀 정보를 심어 저장·삭제 후 원래 화면(`otPcShowPersonDetail`)으로 돌아가게 함.
- `otAttOpenEdit`(날짜 클릭 모달)에 그 날짜의 휴가 상태 배너 추가 — 있으면 수정/삭제, 없으면 부여 버튼.
- 조회 성능을 위해 `otPcShowPersonDetail`이 이미 불러오는 연차 목록에 문서 id를 포함시켜 `_otLeaveCache`에 캐시.
- 상세: `2_8_hr_worktime.md`(관리자 휴가 직접 부여 절).

## 검증

- `node --check`로 전체 스크립트 구문 검증(module/classic 분리).
- jsdom 실행 테스트: 연봉 제안서 회귀 41건 + 기술수당 표시 9건, 근로시간 휴가부여 20건 — 전부 통과.
- 두 레포(production/portal-test) 파일 diff가 Firebase 설정 블록 외에는 완전히 동일함을 확인 후 각각 독립 적용.

## 배포

portal-test 확인 후 production 동시 배포(대표님 "전부 본섭으로 넘겨"). 인사 v2.7.0.

## 백업

`backup/v6.1.0/hr/index.html` (production) — portal-test는 `backup/v2.7.0/hr/index.html`.

## 관련 문서

`2_8_hr_worktime.md`, `2_10_hr_offer.md`, `2_5_hr_payslip_r3.md`(기술수당 산정 기준), `2_7_hr_leave_status_r2.md`(연차 관리자 등록 원본 로직), `8_32_log_2026-09-23_session.md`.
