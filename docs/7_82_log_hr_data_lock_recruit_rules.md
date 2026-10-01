# 7.82. 개발로그 — 인사 데이터 관리자 전용 잠금 + 채용 지원서 비로그인 저장 규칙 (본섭 게시)

> 2026-10-01 · 춘식이(Claude) · 대표님: "(테섭) 확인했어 / 채용 폼은 네가 원하는 대로"

## 배경(발견)
- 인사 컬렉션(근로계약서·연봉계약서·급여명세서·초과근무 등)이 포괄 규칙(승인된 직원 전체 허용)에 걸려, 인사 화면이 관리자 전용이어도 일반 직원이 개발자 도구로 읽고 쓸 수 있었음.
- 홈페이지 채용 폼(recruit.html)은 로그인 없이 `recruit_applicants`에 저장하는데 규칙이 비로그인 저장을 거부해 지원서가 저장되지 않았음(본섭 지원서 0건, 변경 전 규칙도 동일 — 에뮬레이터 확인).

## 변경 (본섭 ruleset 4d39df39…, 이전 4910b897…)
1. **관리자 전용 잠금(15개)**: annual_contracts, labor_contracts, payslips, overtime, company_settings, dismissal_notices, doc_send_log, evaluations, interviews, invoice_history, leave_promotions, payment_history, salary_offers, severance, recruit_applicants — 하위 컬렉션 포함 읽기·쓰기 `isAdmin()`만.
   - payslips는 기획(gihoek) 급여 PJT 배분이 netPay를 읽으므로 `perms.plan` 보유자에게 **읽기만** 추가 허용(현재 해당 비관리자 없음).
2. **채용 지원서 비로그인 저장**: `recruit_applicants` 문서 `create`만 누구나 가능. 허용 항목 17개 한정, name·phone·status·createdAt 필수, `status=='new'`(합격 위조 불가), `createdAt==request.time`(서버 시각), 항목별 길이·목록 개수 제한. 읽기·수정·삭제는 관리자만.
3. 테섭도 같은 규칙(테섭 ruleset c7a227ea…).

## 검증
- 에뮬레이터: 잠금 차분 1332건(판정 변화 417건 전부 의도한 비관리자 차단, 기대와 다른 건 0, 관리자 변화 0), 채용 규칙 26건, 인사 캘린더 62건.
- 본섭 실서버(공개 웹 키·서버 시각, 폼과 동일 방식): 비로그인 정상 저장 200, status=pass 위조 403, 허용 안 된 항목 403, 읽기·목록 403. 시험 문서 3건 삭제 확인(본섭 지원서 0건).
- 대표님이 테섭에서 인사 모듈·기획 급여 배분 정상 확인(잠금 적용 후).

## 백업·롤백
- `backup/rules/20261001_after_hrcal.rules`(직전, ruleset 4910b897…) / `20261001_after_hrdata_lock_recruit.rules`(현재). 이전 규칙으로 되돌리려면 직전 파일을 다시 게시.

## 한계·후속
- 비로그인 저장은 스팸을 규칙만으로 완전히 막을 수 없음(항목·길이 제한만). 스팸이 생기면 지원서 목록에서 삭제하고, 필요 시 App Check·서버 함수 경유로 전환.
- `workers`(근로자 명부)는 잠그지 못함 — 주민번호·계좌·주소·서명이 같은 문서에 있고 PJT·전자결재·기획·모바일이 이름·직급 조회용으로 같은 컬렉션을 읽으며, 전자결재 '내 정보'는 본인 문서를 읽음. 민감 항목을 관리자·본인 전용 문서로 분리하는 개편 필요.
- edoc_* 열람 제한 규칙은 본섭 미게시 상태(결정 대기).
