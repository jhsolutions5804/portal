# 1.4. 기획 — 정산

> Firestore 컬렉션: `gihoek_settlements`
> 최초 작성: 2026-07-01 · 작성: 춘식이(Claude)

---

## Firestore 스키마

```js
gihoek_settlements/{id}:
{
  docType:   'invoice' | 'payment',   // 대금청구서(매출) | 지급예정서(하청 지급)
  no:        string,                  // 문서 번호
  pjtId:     string,
  baseMonth: string,                  // 기준월 'YYYY-MM'
  status:    'active' | 'done' | 'void',
  issueDate: string,
  payDate:   string,                  // 지급요청일/지급예정일
  method:    'progress' | 'qty' | 'manday' | 'manual',
  sender:    {company, ceo, bizno, contact},   // 발신(공급자)
  recipient: {company, ceo, bizno, contact},   // 수신(원청/하청)
  lines:     [{name, spec, amount}],
  supply:    number,   // 공급가
  vat:       number,   // 부가세
  total:     number,   // 합계
  doneAt:    serverTimestamp,
  createdAt: serverTimestamp
}
```

---

## 문서 유형

| docType | 명칭 | 의미 | 완결 처리 |
|---------|------|------|----------|
| `invoice` | 대금청구서 | 원청에 청구(매출) | `doneSettle` → 회계 매출 인식 |
| `payment` | 지급예정서 | 하청에 지급 | `doneSettlePayment` → 회계 직접비(용역비) 반영 |

---

## 상태 정의

| status | 의미 | 집계 |
|--------|------|------|
| `active` | 유효 | ✅ |
| `done` | 완결(청구는 수금, 지급은 송금 완료) | ✅ |
| `void` | 폐기 | ❌ |

`setActive(s)` = 폐기 아님

---

## 지급예정서 → 용역비 자동연동 (N10-1)

지급예정서를 "✓ 지급완료"(`doneSettlePayment`) 처리하면 회계 비용장부의 직접비(용역비)로 자동 반영된다.

**완결 버튼 노출 (정산 상세):**
- `invoice` + active + status≠done → "✓ 완결" (`doneSettle`)
- `payment` + active + status≠done → "✓ 지급완료" (`doneSettlePayment`)
- status===done → "완결 취소" (`undoneSettle`, docType별 메시지 분기)

**자동 반영 로직** (회계 `paymentAsExpense()`):
```
완결된 payment (status==='done' && baseMonth===현재회계월 && setActive)
  → { cat:'용역비'(직접비), vendor:recipient.company, pjt:pjtId,
      supply/vat/total: 정산서 값 그대로, fromSettlement:true }
```
- 비용장부 상세내역에 "🔗 정산 연동" 태그 표시
- 자동 항목 클릭 → `openSettleFromLedger` → 정산 화면으로 이동(수정 불가)
- 지급완료 취소 시 비용장부에서 자동 제외

> ⚠️ 지급예정서는 "지급완료" 처리 전까지는 손익에 반영되지 않는다. (실제 송금 확인 후 반영)
