# 7.61. 개발로그 — 저장된 계약서 근로자 본인 열람 링크 (인사 2.15.0)

> 2026-09-30 · 춘식이(Claude) · 대기열 1번 · **portal-test 배포, 본섭 미반영(대표님 확인 대기)**

## 요구
- 근로자 개인이 본인의 작성 완료된 계약서를 언제든 확인할 수 있는 링크.

## 설계
- 기존 원격 서명 링크(`sign_links`) 구조 재사용 — 규칙 변경 없음(본섭 규칙 그대로 동작).
- 열람 전용 링크: `status:'view'`, `viewOnly:true`. 서명 결과 생성 규칙이 `status=='pending'`을 요구하므로 열람 링크로는 서명 불가.
- 유효기간 180일(서명 링크는 72시간). 본인 확인은 기존과 동일하게 등록된 휴대폰 번호 문자 인증(OTP).
- **양식 동결 원칙 준수**: 링크 생성 시 저장 당시 양식(`tplVer`)으로 렌더링한 HTML(`docHtmlByVer`)만 payload에 저장. 주민번호는 마스킹본, 서명 이미지 포함. `sign.html`은 현재 양식으로 다시 그리지 않고 그대로 표시.
- 대상: 근로계약서·연봉계약서 (연봉제안서·급여명세서는 기존 링크 방식 유지).

## 변경 파일
- `hr/index.html`: `_createDocLink(viewOnly)`, `docViewLink()`, `showSignLinkModal(opts)`, 저장 계약서 조회 화면(근로/연봉)에 "🔗 본인 열람 링크" 버튼.
- `sign.html`: `payload.viewOnly` 처리(저장본 표시), 만료 문구.

## 검증
- Node vm + 모의 Firestore: status=view, 180일, 주민번호 전체 미포함(마스킹만), 서명이미지 포함, offer 요청 거부.
- Chromium 모의 Firebase E2E(sign.html): 폭 390/1280에서 저장본 표시·서명칸 없음·좌우 잘림 없음.
- 실제 문자 인증·실서류 열람은 미확인(대표님 테스트 필요).

## 백업
- portal-test `backup/v2.15.0/hr/`
