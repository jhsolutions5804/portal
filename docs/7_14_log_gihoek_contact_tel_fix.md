# 7.14. 기획 — 거래처 담당자 전화번호 버그 수정 로그

> 작업일: 2026-08-13 · 작성: 춘식이(Claude)

---

## 증상

대표님 리포트: 거래처(업체) 수정 화면에서 담당자 전화번호를 입력하고 저장해도 다시 초기화되는 것처럼 보임.

## 원인

`gihoek/index.html`의 담당자 전화번호 입력 필드:

```html
<input ... oninput="window._cfContacts[i].tel=fmtTel(this.value);this.value=fmtTel(this.value)"
           onblur="fmtTelBlur(this)">
```

`fmtTelBlur(el)`은 8자리 숫자만 입력된 경우(예: `010` 없이 `77367224`) blur 시 자동으로 `010`을 접두하여 **화면에 보이는 `el.value`만** 재포맷했지만, 실제 저장에 쓰이는 `window._cfContacts[i].tel` 배열 값은 갱신하지 않았음.

결과: 화면엔 정상 포맷(`010-7736-7224`)으로 보이지만, `저장` 클릭 시 실제 전송되는 데이터는 이전의 잘못 포맷된 값(`773-672-24`)이 저장됨 → 재진입 시 깨진/이상한 값이 로드되어 "초기화된 것처럼" 보임.

## 수정

- `fmtTelBlur(el)` → `fmtTelBlur(el, idx)`로 인덱스 파라미터 추가
- blur 처리 시 `window._cfContacts[idx].tel`도 함께 갱신
- 호출부: `onblur="fmtTelBlur(this)"` → `onblur="fmtTelBlur(this,${i})"`

## 검증

- Node.js로 타이핑 시뮬레이션 (8자리 입력 → blur) 후 배열/화면 값 일치 확인
- `node --check`로 모듈 스크립트 문법 검증 통과

## 배포

- `gihoek/index.html` 프로덕션 배포 (build 20260813)
- 루트 `index.html` 버전 코멘트: `gihoek 5.3.5` → `5.3.6`
- 백업: `backup/v5.3.7/gihoek/index.html` (수정 전 원본)
- 기능문서: `docs/1_2_gihoek_company.md` → `docs/1_2_gihoek_company_r2.md`
