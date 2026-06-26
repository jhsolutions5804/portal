# 7.3. 개발 로그 — 인사 앱

> `portal/hr/index.html` 변경 이력
> 최초 작성: 2026-06-26 · 최종 수정: 2026-06-27 · 작성: 춘식이(Claude)

---

## 커밋 이력

| SHA | 날짜 | 내용 |
|-----|------|------|
| *(초기)* | 2026-06-24 | 7개 탭: 홈·명부·근로계약·연봉계약·초과근로·급여·퇴직금 |
| *(Rev2)* | 2026-06-25 | 연차 현황 탭(8번) 추가 |
| `2cf3c6996b` | 2026-06-26 | Firebase config 원본 복원 |
| `668d253f` | 2026-06-27 | [D1] hr 내부 사이드바 완전 제거 |
| `6c236d60` | 2026-06-27 | [D2] 명부 PC 레이아웃 + portal_users 드롭다운 연동 |
| `755521e6` | 2026-06-27 | [D3] 명부 v3 — 수정/삭제 복구·서명패드·계약서연동·역방향동기화 |
| `4037f6e3` | 2026-06-27 | [fix] 명부 modal 중첩 백틱 제거 + calcWorkDays·KR_HOLIDAYS 복원 |

---

## [fix] 근로자 상세 모달 오류 수정 (2026-06-27, `4037f6e3`)

### 원인 분석 (로컬 코드 테스트 결과)

**버그 1 — modal.innerHTML 중첩 백틱 (주요 원인)**

`rosterDetail` 함수의 `modal.innerHTML` 구성 시 외부 template literal 안에 내부 백틱을 중첩 사용:

```js
// ❌ 문제 코드
modal.innerHTML = `
  ...
  ${d.hireDate ? `${w.years}년 ${w.months}개월` : '-'}
  ...                ↑ 외부 백틱 내부에 또 백틱
`;
// → 브라우저가 내부 백틱을 template literal 종료로 오인
// → modal.innerHTML 전체 파싱 실패 → 모달 열리지 않음
```

```js
// ✅ 수정 코드 — 문자열 연결 방식으로 교체
${d.hireDate ? (w.years>0?w.years+'년 ':'')+w.months+'개월 ('+w.calDays+'일)' : '-'}
```

**버그 2 — calcWorkDays + KR_HOLIDAYS 누락**

D3 배포 시 명부 섹션 코드 교체 범위(L2304~L2836)에 `KR_HOLIDAYS` 상수와 `calcWorkDays` 함수가 포함되어 있었으나 새 `roster_v3.js`에 해당 함수가 없어 통째로 사라짐.

- `rosterDetail`에서 `calcWorkDays ? ... : fallback` 삼항으로 방어되어 있어 ReferenceError는 발생하지 않았으나 재직기간·실 근무일수 항상 0 표시
- 퇴직금 탭(`renderRetireMain`)에서도 `calcWorkDays` 호출 → 퇴직금 계산 오류

**수정**: 원본 백업에서 두 함수 블록을 추출해 `window.rosterDetail` 정의 직전에 복원

### 교훈

- `modal.innerHTML = \`...\`` 같은 외부 template literal 안에서 조건부 텍스트 생성 시 내부 백틱 절대 사용 금지 → 문자열 연결(`+`) 방식 사용
- 코드 섹션 교체 시 해당 범위 안에 **다른 기능의 공유 함수**가 포함되어 있는지 반드시 확인

---

## 이전 변경 상세 (D1~D3)

### D1 — hr 내부 사이드바 완전 제거
- `<aside id="hr-sidebar">` HTML 블록 + 관련 CSS 전체 삭제

### D2 — 명부 PC 레이아웃 + portal_users 연동
- 탭 진입 즉시 명단 테이블 표시 / 우측 상단 신규 등록 버튼
- portal_users 드롭다운 → 이름·직급·부서 자동 채움

### D3 — 명부 v3 전면 개선
- 수정/삭제 모달 복구
- 개인 서명 패드 (canvas, workers.signData 저장)
- `window.getWorkerData(workerId)` 전역 함수 등록 (계약서 연동 준비)
- 저장 시 portal_users 역방향 동기화 (name·rank·dept·empNo)

---

## 이슈 & 해결

| 이슈 | 원인 | 해결 |
|------|------|------|
| 근로자 상세 모달 열리지 않음 | modal.innerHTML 내 중첩 백틱 | 문자열 연결 방식으로 교체 |
| 재직기간·실근무일수 0 표시 | calcWorkDays 함수 누락 | 원본에서 복원 |
| Firebase messagingSenderId 오류 | 0 하나 추가된 오염값 | 원본 11자리로 복원 |
| hr 앱 내부 사이드바 포털과 중복 | 사이드바 HTML·CSS 완전 제거 |  |
