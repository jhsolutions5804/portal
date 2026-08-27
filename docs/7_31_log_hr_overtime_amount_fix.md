# 7.31. 개발로그 — 인사 초과근로 누계/총 수당 금액 표시 정정 (2026-08-27)

## 배경
대표님이 인사(HR) 모듈 초과근로 화면 스크린샷을 공유하며 "누계수당 뭉뚱그리지 말고 금액 정확하게 1원까지" 요청.
스크린샷 확인 결과 "누계 수당" 카드에 `13만원`으로 표시되었으나, 하단 상세 테이블 합산 실제값은 128,730원으로 만원 단위 반올림 표시였음.

## 원인
`hr/index.html` 내 두 곳의 `fmt` 헬퍼가 10,000원 이상일 때 `Math.round(v/10000)+'만원'` 형태로 반올림:
- `otPcLoadKpiAndHours` (상단 KPI "총 수당")
- `otPcShowPersonDetail` (개별 직원 상세 패널 "누계 수당")

모바일 뷰(`otLoadPersonDetail` 등)는 원래 `toLocaleString()` 방식이라 문제 없었음.

## 조치
두 `fmt` 함수를 모두 `v => v.toLocaleString()+'원'`으로 교체하여 1,000단위 콤마 + 1원 단위 정확 표시로 통일 (포털 전체 금액 표시 컨벤션과 일치).

## 검증
- `node --check`로 5개 `<script>` 블록 전체 문법 검증 통과 (module import → null 치환 후 `.mjs`로 검사)
- 변경 전/후 diff로 의도치 않은 변경 없음 확인

## 배포
- 대표님 지시: "테섭하고 본섭 다 배포해" — 사전 확인 절차 생략 승인으로 판단, 양쪽 동시 배포
- production(`portal`): fresh SHA 재확인 후 배포
- portal-test(`portal-test`): production 편집본을 그대로 복사하지 않고, test repo `hr/index.html`을 독립적으로 fresh fetch → 동일 패치 3건 개별 적용 → `firebaseConfig` 블록 regex 보존 확인 후 배포
- 양쪽 모두 Contents API로 반영 여부(`toLocaleString` 적용, 만원 반올림 코드 부재, 버전 주석) 확인 완료

## 버전
- `hr/index.html`에 버전 주석 신규 추가: `<!-- HR module build: 20260827a · ver 1.0.1 · ... -->` (기존 hr 모듈에는 버전 주석이 없었음 — 이번 건부터 트래킹 시작)
- 백업: `backup/v1.0.1/hr/index.html` (production 신규본 스냅샷)

## 관련 파일
- `hr/index.html` (production, portal-test)
- `docs/2_4_hr_overtime_r2.md` (문서 갱신)
