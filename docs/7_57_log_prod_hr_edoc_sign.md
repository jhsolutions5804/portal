# 7.57. 개발로그 — 본섭 반영: 인사 2.14.0 · 전자결재 · 원격 서명(sign.html)

> 2026-09-30 · 춘식이(Claude) · 대표님 지시

## 선행 (대표님 콘솔 작업)
- Blaze 전환(무료 체험판), Authentication 전화 로그인 활성화, 승인 도메인 `portal.jhsol.kr` 등록, SMS 리전 정책 KR 허용.
- 본섭 Firestore 규칙 step2 게시(= step1 + `sign_links`·`sign_links/{token}/secure` 규칙). 게시본 일치 확인.

## 반영 파일 (테섭 파일 + Firebase 설정만 본섭 값으로 교체)
- `sign.html`(신규), `hr/index.html`(2.14.0; `_SIGN_BASE`를 `https://portal.jhsol.kr/sign.html`로 변경), `edoc/index.html`, `m/edoc.html`, `index.html`(포털 홈 전체 동기화), `m/home.html`.
- 백업: `backup/v_sign_20260930/`, `backup/v2.14.0/hr/`, `backup/v_edoc_20260930/`, `backup/v_home_20260930b/`

## 미반영·주의
- `edoc_*` 열람 제한 규칙은 아직 미게시(별도 결정).
- 문서 이메일 자동발송(EmailJS)은 Public Key·Template ID 미설정 — 실사용 불가.
- 최초 로그인 휴대폰 인증은 `PHONE_VERIFY_REQUIRED=false`로 꺼둔 상태(기능 코드만 포함).
- 원격 서명 링크는 받는 사람 휴대폰 번호가 없으면 생성이 거부됨.
- `pjt_ph4`(SUP 종료)와 테섭 전용 `attendance/`, `tools/`는 미반영.
