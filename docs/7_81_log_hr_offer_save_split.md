# 7.81. 개발로그 — 연봉 제안서 저장/출력 분리 (hr 2.23.1)

> 2026-10-01 · 춘식이(Claude) · **portal-test 적용, 본섭 대기**

## 증상
- 출력(PDF) 또는 이메일 발송을 누르면 무조건 `salary_offers`에 새 문서가 추가되고 인사 캘린더에 회신기한이 자동 등록됨. 테스트 출력도 그대로 반영.

## 원인
- 저장 동작이 별도로 없고 `offerPrint`/`offerSendEmail` 안에서 `addDoc` + `_offerCalSync`를 호출. 일정 ID에 제안일이 포함되어 재출력 시 중복 생성, 이력은 재출력마다 새 건.

## 수정 (`hr/index.html`)
- `offerPrint`: 저장·캘린더 제거(미리보기 전용). 신규 `offerSave`/`_offerSaveDoc`(신규 addDoc → 이후 setDoc merge, `_id` 보관), `_offerCalSync`는 `offerreply_<문서ID>` 기준·회신기한 비면 삭제, `offerSendEmail`은 `_offerSaveDoc` 후 발송, 지난 제안서에 `offerEditObj`, 상태 표시 `_offerStateHtml`.
- 규칙: `salary_offers`는 별도 match 없이 승인 계정 catch-all이라 setDoc(수정) 허용 — 규칙 변경 없음.

## 검증
- JS 문법(node --check), CSS 괄호 0. 모의 Firestore 시나리오: 출력만→문서 0·일정 0 / 저장→문서 1·일정 1 / 수정 후 재저장→덮어쓰기·같은 일정 갱신 / 이메일 발송→같은 문서 ID 사용 / 회신기한 비움→일정 삭제.
- portal-test 반영 후 화면 확인 필요. 테섭↔본섭 hr 차이는 Firebase·EmailJS·서명 URL 설정뿐(패치는 양쪽 독립 적용 가능).

백업: portal-test `backup/v2.23.1/hr/index.html`
