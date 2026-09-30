# 7.58. 개발로그 — 인사 2.14.1 문서 이메일 발송(EmailJS) 설정

> 2026-09-30 · 춘식이(Claude)

- HTTPS 강제(GitHub Pages) 후 서명 링크 생성 정상화 확인(문자 인증 수신 확인).
- EmailJS 값 반영: Service ID `service_7iova18`(Outlook), Template ID `template_jto208l`, Public Key(공개용, 코드에 포함). 템플릿 변수: to_email, to_name, doc_label, company_name, link.
- Private Key는 사용하지 않으며 코드·문서에 넣지 않음.
- 무료 요금제 월 200통. 백업: `backup/v2.14.1/hr/`
- 미확인: 실제 발송 테스트 결과.
