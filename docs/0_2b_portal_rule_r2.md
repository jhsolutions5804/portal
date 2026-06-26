# 0.2b. 포털 기본 Rule — 코드 주의사항·공통 로직

> 최초 작성: 2026-06-26 · 최종 수정: 2026-06-27 · 작성: 춘식이(Claude)
> 연속 문서: 0.2a (디자인·레이아웃·배포)

---

## HTML 코드 작성 주의사항

### ⚠️ 중첩 백틱 절대 금지 (2026-06-27 추가)

`innerHTML`, `modal.innerHTML` 등 외부 template literal 내부에서 다시 백틱 사용 금지.

```js
// ❌ 절대 금지 — 브라우저가 내부 백틱에서 template literal 종료로 오인
modal.innerHTML = `
  <span>${condition ? `내부 템플릿` : '-'}</span>
`;

// ✅ 올바른 방식 — 문자열 연결(+) 사용
modal.innerHTML = `
  <span>${condition ? '텍스트' + variable + '텍스트' : '-'}</span>
`;
```

> 이 버그의 증상: 모달이 열리지 않거나 innerHTML 이후 코드가 실행되지 않음.
> JS 문법 검증(`node --check`)에서 잡히지 않고 런타임에서만 나타남.

### `<script type="module">` 내 inline onclick 규칙

module scope 함수는 inline `onclick` 속성에서 직접 접근 불가. 반드시 `window.fn = fn`으로 전역 등록 필수.

```js
// ❌ 접근 불가
function myFunc() { ... }
// html: onclick="myFunc()" → ReferenceError

// ✅ 올바른 방식
window.myFunc = function() { ... }
// html: onclick="myFunc()" → 정상 동작
```

### 코드 섹션 교체 시 공유 함수 보존

특정 섹션(예: 근로자 명부) 코드를 교체할 때, 그 범위 안에 **다른 탭이 공유하는 함수**가 포함되어 있을 수 있다.

교체 전 반드시 교체 범위를 grep으로 확인하여 공유 함수가 새 코드에도 포함되어 있는지 검증한다.

```bash
# 교체 범위 내 함수 목록 확인
sed -n '{START},{END}p' index.html | grep -n "^function\|^window\.\|^const\|^let\|^async function"
```

> 실제 사례: `KR_HOLIDAYS` + `calcWorkDays`가 명부 섹션 내 위치 → 명부 교체 시 누락 → 퇴직금 탭 파손

---

## 공통 비즈니스 로직

### 근로기준법 연차 계산 (edoc·hr 공통)
```js
// 1년 미만: 1개월 개근당 1일 (최대 11일)
// 1년 이상: 15일
// 3년 이상: 15 + floor((근속년수-1)/2), 최대 25일
calcAnnualLeaveGrant(hireDate, baseDate=오늘) → {granted, years, months, detail}
sumLeaveUsed(leaveDocs, name) // posted/approved 연차 days 합산
```
- edoc: `calcAnnualLeaveGrant` / hr: `hrCalcAnnualLeave` (동일 로직, **양쪽 동시 수정 필요**)

### A4 출력 (`printDocA4(d, dtype)`)
- `window.open` 새 창에 A4 HTML 작성 → 자동 `window.print()`
- `@page{size:A4;margin:18mm}`, `<\/script>` 이스케이프 필수

### 고정 결재라인 (`buildFixedApprovalLine(dtype)`)
- DOC_CONFIG에 `approvers:[이름…]`, `cc:[이름…]` 지정
- `findUserByName`으로 portal_users에서 uid 매핑
- 고정 결재자는 portal_users 계정 존재 필수

---

## 전화번호 포맷 공통 함수 (F1, 2026-06-26)

모든 앱의 전화번호 입력 필드에 공통 적용.

```js
function fmtTel(v){
  var d=v.replace(/\D/g,'');
  if(d.length<=3) return d;
  if(d.length<=6) return d.slice(0,3)+'-'+d.slice(3);
  if(d.length<=10) return d.slice(0,3)+'-'+d.slice(3,6)+'-'+d.slice(6);
  return d.slice(0,3)+'-'+d.slice(3,7)+'-'+d.slice(7,11);
}
function fmtTelBlur(el){
  var d=el.value.replace(/\D/g,'');
  if(d.length===8 && d[0]!=='0') d='010'+d;
  el.value=fmtTel(d);
}
```

적용: `oninput="this.value=fmtTel(this.value)"` + `onblur="fmtTelBlur(this)"` + `maxlength="13"`

| 앱 | 필드 |
|----|------|
| portal | 내 정보·직원 상세 전화번호 |
| gihoek | 거래처 담당자 전화번호 |
| hr | 근로자 명부 신규폼·수정모달 |
| edoc | 연차신청 비상연락처 |
