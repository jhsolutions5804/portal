# 7.15. 기획 — 거래처 담당자 전화번호 저장 안 되던 진짜 원인 수정 로그

> 작업일: 2026-08-13 · 작성: 춘식이(Claude)

---

## 경위

`7_14_log_gihoek_contact_tel_fix.md`에서 blur 시 배열 미동기화 버그를 수정해 배포했으나, 대표님 재확인 결과 여전히 담당자 전화번호가 저장되지 않음(저장 후 목록에서 재확인 시 초기화). "저장했습니다" 토스트조차 뜨지 않음.

## 진짜 원인 (브라우저 콘솔 확인)

대표님이 캡처해주신 콘솔 로그:

```
Uncaught ReferenceError: fmtTelBlur is not defined
    at HTMLInputElement.onblur
Uncaught ReferenceError: fmtTel is not defined
    at HTMLInputElement.oninput
```

`gihoek/index.html`은 전체가 단일 `<script type="module">` 블록으로 작성되어 있음. 모듈 스크립트 내부의 최상위 `function fmtTel(){...}`, `function fmtTelBlur(){...}` 선언은 **모듈 스코프에만 존재**하며, `window` 객체에 자동으로 노출되지 않음.

반면 HTML 인라인 이벤트 핸들러(`oninput="..."`, `onblur="..."`)는 **전역(글로벌) 스코프**에서 실행되므로, 모듈 스코프 함수는 여기서 보이지 않음 → `ReferenceError`.

즉, 담당자 전화번호 입력란에 글자를 입력하는 순간부터 이미 에러가 나서 `window._cfContacts[i].tel`에 값이 전혀 반영되지 않고 있었음. r2에서 고친 blur-배열 동기화 버그는 애초에 도달하지도 못하는 코드였음.

## 왜 첫 번째 담당자(이경택 차장님)는 전화번호가 저장되어 있었나?

기존 데이터는 이 버그가 생기기 이전(또는 다른 경로)로 저장된 것으로 추정. 버그 자체는 이 필드에 새로 입력/수정을 시도하는 모든 경우에 적용됨.

## 전수 조사

파일 내 모든 인라인 이벤트 핸들러(`on\w+="..."`)에서 호출하는 함수명을 추출해 `window.X=` 노출 여부를 대조:

```python
handlers = re.findall(r'on\w+="([^"]*)"', content)
calls = {func names called inside handlers}
window_exposed = {names in `window.X=` assignments}
missing = calls - window_exposed
# → ['fmtTel', 'fmtTelBlur', 'zoneGuess']
```

`zoneGuess`는 `onchange="toggleSetEst('${e.id}','${zoneGuess(e.title)}')"` 형태로, 템플릿 문자열 생성 시점(모듈 스코프 안에서 `${}` 평가)에 이미 값으로 치환되므로 실제로는 문제 없음(false positive). `fmtTel`, `fmtTelBlur` 두 개만 실제 버그.

## 수정

```js
function fmtTel(v){ ... }
window.fmtTel=fmtTel;
function fmtTelBlur(el,idx){ ... }
window.fmtTelBlur=fmtTelBlur;
```

## 검증

- `node --check`로 모듈 스크립트 문법 검증 통과
- GitHub API(`contents`) 및 raw.githubusercontent.com으로 배포된 코드에 `window.fmtTel`, `window.fmtTelBlur` 존재 확인

## 배포

- `gihoek/index.html` 프로덕션 배포
- 루트 `index.html` 버전 코멘트: `gihoek 5.3.6` → `5.3.7`
- 백업: `backup/v5.3.8/gihoek/index.html` (수정 전 원본)
- 기능문서: `docs/1_2_gihoek_company_r2.md` → `docs/1_2_gihoek_company_r3.md`

## 교훈 (향후 재발 방지)

`<script type="module">` 안에서 HTML 인라인 이벤트 핸들러(`onclick`/`oninput`/`onchange`/`onblur`)에서 호출하는 함수는 **반드시 `window.X = X` 형태로 명시적 전역 노출이 필요**함. 새 함수를 추가하고 인라인 핸들러에서 쓸 때마다 이 점을 빠뜨리지 않도록 주의. 다른 모듈(edoc, hr, pjt, pjt_ph4)도 동일 패턴 취약점이 있을 수 있어 필요 시 같은 방식으로 전수 조사 가능.
