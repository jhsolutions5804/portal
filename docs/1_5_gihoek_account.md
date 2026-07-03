# 1.5. 기획 — 회계

> Firestore 컬렉션: `gihoek_expenses` (+ 읽기: `gihoek_settlements`, `workers`, `payslips`)
> 최초 작성: 2026-07-01 · 최종 개정: 2026-07-02 (r2) · 작성: 춘식이(Claude)

---

## Firestore 스키마

```js
gihoek_expenses/{id}:
{
  date:    string,    // 'YYYY-MM-DD' — 회계 반영월의 기준
  cat:     string,    // ACC_CATS 중 하나
  vendor:  string,    // 거래처/가맹점 (급여배분은 직원명)
  supply:  number, vat: number, total: number,
  pay:     string,    // 결제수단 (ACC_PAYS)
  pjt:     string, note: string,
  // 급여배분(N10-2) 전용: salaryDist, workerId, salBaseMonth, baseMonth
  createdAt: serverTimestamp
}
```

---

## 카테고리 / 결제수단

```js
ACC_CATS = [식대, 유류비, 공구·자재비, 차량유지비, 사무용품, 기타, 임대료, 세금, 급여, 용역비]
ACC_PAYS = [법인카드, 개인카드, 현금, 계좌이체, 외상거래]   // ← '외상거래' 추가 (2026-07-02)
DIRECT_CATS = ['급여', '용역비', '공구·자재비']   // 직접비
```

- **직접비**: 급여 · 용역비 · 공구·자재비 / **간접비**: 나머지

---

## 손익 계산

```
영업이익 = 매출(기준월 완결 청구) − 직접비 − 간접비
```

- 매출: `monthBill(pid, month)` — 완결(done) 대금청구서 합
- 월 비용: `accMonthExp()` = 수동입력 + `paymentAsExpense()`(완결 지급예정서)
- PJT별 손익표 + 공통비용(PJT 미지정) 별도

---

## 두 서브탭

| 서브탭 | 함수 | 내용 |
|--------|------|------|
| 영업이익 현황 | `renderAccPnl` | 매출·직접비·간접비·영업이익, PJT별 손익 |
| 비용 장부 | `renderAccLedger` | 카테고리별 집계, 상세내역(필터), 비용입력·급여배분 버튼 |

---

## 상세내역 필터 (r2, 2026-07-02 신규)

비용 장부의 상세내역 상단에 필터 바(`_filterBar`) 추가. 월 전체 집계·요약은 유지하고 **상세내역 목록만** 필터/정렬한다.

| 필터 | 상태 변수 | 옵션 |
|------|-----------|------|
| 정렬 | `accLSort` | 날짜 오름차순(`date_asc`) / 내림차순(`date_desc`) |
| 항목 | `accLCat` | 전체 / `ACC_CATS` 중 선택 |
| 거래처 | `accLVendor` | 전체 / 현재 월 내 거래처(vendor) 유니크 목록 |

- 핸들러: `accSetFilter(k,v)` — 상태 갱신 후 `renderAccLedger()` 재호출 / `accResetFilter()` — 초기화
- 조건 걸리면 `필터 초기화` 버튼 노출, 결과 없으면 "조건에 맞는 내역이 없습니다" 안내

---

## 비용 입력 (수동)

- `accOpenForm` — 날짜·카테고리·거래처·금액·PJT·결제수단·비고
- 합계 → 공급가·부가세 역산(`accSplitVat`), 면세(`accZeroVat`)
- **등록창 위치 (r2, 2026-07-02)**: 기존 하단 바텀시트(`.emodal{align-items:flex-end}`, `.esheet{border-radius:16px 16px 0 0}`)에서 **화면 중앙 카드**(`align-items:center`, `border-radius:16px`, 상하좌우 여백)로 변경 — "바닥에 붙는" 느낌 해소
- `accSave` / `accDel`

---

## 급여 PJT 비율배분 (N10-2)

비용장부의 "👥 급여 배분" 버튼으로 급여명세서 실지급액(netPay)을 PJT별로 나눠 직접비(급여)에 반영. id `salary_{wid}_{기준월}_{pjt}`, 회계 반영월 = 급여일(기준월 익월 말일)이 속한 월. 저장 전 동일 직원·기준월 항목 전체 삭제 후 재작성.
