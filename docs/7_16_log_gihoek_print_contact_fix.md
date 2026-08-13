# 7.16. 기획 — 견적/정산 인쇄 시 담당자 전화번호 오표시 수정 로그

> 작업일: 2026-08-13 · 작성: 춘식이(Claude)

---

## 증상

견적서 작성 시 담당자를 "배민철 부장님"으로 선택했는데, 인쇄/PDF 출력물에는 다른 사람(이경택 차장님)의 전화번호가 표시됨. 앱 내 견적 상세 화면(`partyHtml`)에는 "담당: 배민철 부장님"으로 정확히 표시되고 있었음.

## 원인

`printEst()` 함수의 "공급받는자" pcard 템플릿:

```js
${cl.tel?`<div class="ln">${cl.tel}</div>`:''}
```

`cl.tel`은 견적 저장 시 스냅샷된 **거래처(업체) 레벨의 레거시 `tel` 필드**(담당자 여러 명을 지원하기 전, 업체 단위로 저장돼 있던 옛 전화번호)를 가리킴. 반면 실제로 견적에서 선택한 담당자 정보는 `ctSnap()`을 통해 `client.contact`(담당자명), `client.contactTel`(담당자 전화번호)에 별도로 스냅샷되어 있었는데, 인쇄 템플릿은 이 필드를 전혀 참조하지 않았음.

발행처(공급자) 쪽은 하단 도장란에서 `iss.contact`/`iss.contactTel`을 올바르게 사용하고 있었으나, 수신처(공급받는자) 쪽 카드에는 대응 로직이 누락돼 있었음 — 견적서/정산서 두 문서 모두 동일 패턴.

정산서 인쇄(`settleDocHTML`)의 "수신" 카드도 동일하게 `rc.tel`(레거시)만 쓰고 `rc.contact`/`rc.contactTel`은 무시하던 동일 버그.

## 수정

**견적서 (`printEst`, 공급받는자 카드):**
```js
${cl.contact?`<div class="ln">${cl.contactTel?cl.contactTel+' ':''}(${cl.contact})</div>`:(cl.tel?`<div class="ln">${cl.tel}</div>`:'')}
```

**정산서 (`settleDocHTML`, 수신 카드):**
```js
${rc.contact?`<div class="ln">${rc.contactTel?rc.contactTel+' ':''}(${rc.contact})</div>`:(rc.tel?`<div class="ln">${rc.tel}</div>`:'')}
```

담당자가 선택된 경우 담당자 전화번호+이름을 우선 표시, 선택 안 된 경우 기존처럼 업체 레거시 tel로 폴백.

## 검증

- `node --check` 문법 검증 통과
- 배포 전/후 diff로 의도한 두 줄만 변경됐는지 확인

## 배포

- `gihoek/index.html` (build 20260813c)
- 루트 `index.html` 버전 코멘트: gihoek 5.3.7 → 5.3.8
- 백업: `backup/v5.3.9/gihoek/index.html`
- 기능문서: `docs/1_3_gihoek_estimate_r3.md` → `docs/1_3_gihoek_estimate_r5.md`
