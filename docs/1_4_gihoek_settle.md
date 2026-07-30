# 1.4. 기획 — 정산

> Firestore 컬렉션: `gihoek_settlements`
> 최초 작성: 2026-07-01 · 최종 수정: 2026-07-30(r4) · 작성: 춘식이(Claude)

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

---

## 지급예정서 회계 계상월 — 1.4.x

지급예정서(payment)가 회계 장부에 계상되는 월(`acctMonth`). 급여와 동일 규칙.

- 기준: **지급예정일(payDate)** 의 월. 지급예정일 비면 `defaultPayDate(기준월)` = 익월 말일(주말→금요일 보정) 자동
- `acctMonthOf(s)`: 저장된 `acctMonth` 우선 → 없으면 payDate→issueDate→baseMonth 폴백(하위호환)
- 발행 시 `acctMonth` 저장. 상세보기에서 표시 + 수정 버튼(`editAcctMonth`, YYYY-MM prompt)
- 회계 반영(`paymentAsExpense`)은 `acctMonth` 기준으로 해당 월 집계


---

## UI — 금액 입력 포맷 (r2, 2026-07-23)

기술인력 단가, 직접입력 정산 품목(단가·금액) 입력창에 실시간 콤마 포맷(`fmtMoney(el)`) 적용(1000단위마다 `,`). 상세: `7_2_log_gihoek_r5.md`

---

## 정산 방식 — 공정 연동(progress)의 구역(zone) 자동인식 — 1.4.x (r3, 2026-07-30)

`method:'progress'`(공정 연동)로 정산서를 작성할 때, 견적 항목을 체크하면 `zoneGuess(title)`가 항목명에 포함된 키워드로 구역(zone)을 자동 판정한다. (예: "3F FIZ", "복합3동", "X-OB" 등 — `PROGRESS_PROFILES[프로젝트].zones`에 정의)

- 판정 방식: `zones` 배열을 순서대로 검사해 **키워드가 처음 매치되는 zone**으로 확정 (first-match)
- **주의(2026-07-30 버그 수정)**: 견적 항목명에 건물명(예: "복합4동")과 설비타입(예: "3F FIZ")이 함께 들어가는 경우가 있음 (예: "복합4동 3F FIZ FCU 14대 설치"). 이때 `zones` 배열에서 설비타입 zone("3F FIZ")이 건물명 zone("복합4동")보다 먼저 나오면, 실제로는 복합4동(14대)인 항목이 3F FIZ(39대)로 잘못 배정되어 반입/설치 진행률이 엉뚱한 총 수량(39) 기준으로 표시되는 문제가 있었다.
- **수정**: `PROGRESS_PROFILES.p4ph2.zones` 배열 순서를 건물명 zone(복합3동·복합4동)이 설비타입 zone(3F FIZ 등)보다 **먼저 오도록** 재배치. `zoneGuess` 로직 자체는 유지(first-match).
- ⚠️ 자동 인식은 **신규 체크 시점**에만 적용된다. 기존에 이미 잘못 배정되어 저장된 정산서(`estZone`)는 자동 반영되지 않으므로, 정산서 상세 화면의 구역 선택 드롭다운(`setZone`)으로 수동 재선택 필요.
- 향후 zone을 추가할 때는 항목명에 건물명/구역명이 설비타입명과 함께 쓰일 가능성을 고려해, **더 구체적인(건물·구역 고유명) 키워드를 배열 앞쪽에** 배치할 것.

---

## 공급가액·부가세 수동 수정 — 1.4.x (r4, 2026-07-30)

정산서 작성 화면 하단 합계 박스(공급가액/부가세)를 직접 입력으로 수정할 수 있다.

- 기본값은 정산 방식(공정/수량/공수/직접입력)에 따라 자동 계산된 값(`setSupply()`)이며, 부가세는 공급가액의 10%
- 공급가액 또는 부가세 입력창에 직접 값을 입력하면 `settleDraft.supplyOverride` / `vatOverride`에 저장되어 그 값이 우선 적용됨(`effSupply()`/`effVat()`)
- 수동 수정된 상태에서는 "✎ 수동 수정됨" 안내와 함께 자동계산값을 같이 표시, "자동계산으로 되돌리기" 링크로 오버라이드 해제 가능
- 발행(`publishSettle`) 시 오버라이드된 값 그대로 `gihoek_settlements`에 저장됨 (`supply`, `vat`, `total`)
- ⚠️ 오버라이드는 견적/공수 등 원본 항목을 수정해도 자동으로 재계산되지 않고 유지됨 — 원본 데이터를 바꾼 뒤에는 필요 시 "자동계산으로 되돌리기"로 재확인할 것

---

## 공수 연동(manday) 자동집계 오차 수정 — 1.4.x (r4, 2026-07-30)

**문제**: `fetchManday()`가 `worker_manday`/`ph4_manday` 컬렉션의 일별 문서에서 `md` 객체 값을 **무조건 전부 합산**하고 있어, 월간 공수 집계 화면(`pjt_manday`)의 PJT별 합계보다 큰 값이 표시되는 경우가 있었다. (예: SUP 7월 실제 8.0공수인데 정산서엔 19.6공수로 집계)

**원인**: `pjt_manday` 화면은 합산 시 해당 근로자 ID가 **현재 유효한 명부**(`pjt_workers_fab`/`pjt_workers_ph4`)에 있는 경우만 카운트하고, 명부에 없는 ID(근로자 정리·중복 통합·오입력 등으로 남은 잔재 데이터)는 무시한다. 반면 `gihoek`의 `fetchManday()`는 이런 필터링 없이 일별 문서의 `md` 값을 전부 더했기 때문에 두 화면의 집계 기준이 달라 수치가 어긋났다.

**수정**: `fetchManday()`도 동일하게 프로젝트에 연동된 명부 컬렉션(FAB→`pjt_workers_fab`, SUP→`pjt_workers_ph4`)을 조회해 ID셋을 만들고, 그 안에 있는 ID의 공수만 합산하도록 변경. 명부 외 ID의 공수는 제외되며, 있을 경우 완료 토스트에 "(명부 외 N 공수 제외)"로 안내.

