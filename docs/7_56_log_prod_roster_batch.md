# 7.56. 개발로그 — 본섭 일괄 반영 (연명부·월간 공수·기획 정산·포털 홈)

> 2026-09-30 · 춘식이(Claude) · 대표님 지시로 테섭 검증분 본섭 반영

## 순서
1. 본섭 Firestore 규칙 게시 (대표님이 콘솔에서 직접) — `master_worker_private`·`master_worker_photos` 관리자 전용 + catch-all에서 제외. 게시본 = `firestore.rules.prod_step1` 과 일치 확인.
2. 금액 이전 1단계(복사): master_workers.{teamRate,dailyRate} → master_worker_private (13명, 14필드, 충돌 0).
3. 코드 반영: `pjt_manday` 1.2.0 · `pjt_roster` 1.5.0(신규) · `gihoek` 5.9.0 · 포털 홈(연명부 메뉴만 선별 반영).
4. 금액 이전 2단계(옛 위치 제거): master_workers 금액 필드 제거, 잔여 0 확인.

## 비고
- 각 파일은 테섭 파일에서 Firebase 설정만 본섭 값으로 교체해 반영(`portal-test` 문자열 잔존 0 검사).
- 포털 홈은 테섭 전체가 아니라 연명부 메뉴·관리자 접근 제한 부분만 선별 반영(인사 메뉴 개편·강제 PC 모드·휴대폰 인증 등은 미반영).
- 백업: `backup/v1.2.0/pjt_manday/`, `backup/v_pjt_roster_20260930/`, `backup/v5.9.0/gihoek/`, `backup/v_home_20260930/`
- 미반영(결정 대기): 인사 2.14.0, 전자결재/모바일 전자결재(회계연도 연차), 원격 서명(sign.html)+sign_links 규칙, edoc_* 열람 규칙, 모바일 홈 문구.
