# 7.4b. 개발로그 — 전자결재 (금액 콤마 포맷, 2026-07-23~)

> `7_4_log_edoc.md`가 200줄을 초과해 이어서 작성. 이전 이력은 `7_4_log_edoc.md` 참고.

---

## 2026-07-23 세션 — 금액 입력창 1000단위 콤마 포맷 적용

### 배경
대표님 지시: "포탈 내 모든 금액 입력·출력은 1000단위마다 콤마(,) 표시" (전 모듈 공통 UI 컨벤션)

### 변경 내용
`DOC_CONFIG`의 구매품의서 `unitPrice`, 지출결의서 `amount` 필드 타입을 기존 `'number'`에서 신설한 `'money'`로 변경:
- 렌더러(`renderDocForm` 내 필드 생성 분기)에 `f.type==='money'` 케이스 추가 — `type="text" inputmode="numeric"` + `oninput="fmtMoney(this)"`로 실시간 콤마 표시
- `docSave`에도 `f.type==='money'` 분기 추가 — 저장 시 콤마·비숫자 문자를 제거한 뒤 `Number()`로 변환해 저장(기존 `number` 타입은 `el.value`를 그대로 저장하던 구조라, 콤마가 섞이면 문자열로 잘못 저장될 위험이 있어 별도 파싱 필요했음)
- 상세보기(`docDetail`)도 `f.type==='money'`인 필드는 `Number(v).toLocaleString('ko-KR')+'원'` 형식으로 표시하도록 분기 추가
- 초과근로(overtime)의 수당(`amount`)/통상임금(`rate`)은 `DOC_CONFIG`상 `type:'number'`로 남아있으나, 실제 사용자 입력 폼(`renderOvertimeWrite`)은 이 설정을 쓰지 않고 근로자 등록 시급 기준 자동계산이라 사용자가 직접 타이핑하는 금액 입력창이 아님 — 콤마 포맷 대상에서 제외(현행 유지)

전역 헬퍼 `window.fmtMoney(el)` 신설(gihoek/hr과 동일 로직).

### 검증
- `node --check`로 모듈 스크립트(.mjs 추출) 문법 검증 통과

### 배포
- portal-test 선배포(기존 test 원본의 사소한 차이 — 초과근로 목록 `authorUid` 필터 미적용 상태 — 보존한 채로 개별 패치 적용) → 대표님 확인("오케이") → production 배포
- production: `edoc/index.html` 배포 완료, Pages 빌드 `built` 확인

### 문서
- `docs/3_3_edoc_docs.md` r2 갱신
