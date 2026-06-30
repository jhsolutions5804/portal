# 1.5. 기획 — 회계

> Firestore 컬렉션: `gihoek_expenses` (+ 읽기: `gihoek_settlements`, `workers`, `payslips`)
> 최초 작성: 2026-07-01 · 작성: 춘식이(Claude)

---

## Firestore 스키마

```js
gihoek_expenses/{id}:
{
  date:    string,    // 'YYYY-MM-DD' — 회계 반영월의 기준
  cat:     string,    // ACC_CATS 중 하나
  vendor:  string,    // 거래처/가맹점 (급여배분은 직원명)
  supply:  number,    // 공급가
  vat:     number,    // 부가세
  total:   number,    // 합계
  pay:     string,    // 결제수단
  pjt:     string,    // PJT id (없으면 공통비용)
  note:    string,
  // ── 급여배분(N10-2) 전용 필드 ──
  salaryDist:  boolean,   // true면 급여배분 항목
  workerId:    string,    // 근로자 id
  salBaseMonth:string,    // 급여 기준월 'YYYY-MM'
  baseMonth:   string,    // 회계 반영월 'YYYY-MM' (= 급여일이 속한 월)
  createdAt:   serverTimestamp
}
```

---

## 카테고리 / 직접비·간접비

```js
ACC_CATS = [식대, 유류비, 공구·자재비, 차량유지비, 사무용품, 기타, 임대료, 세금, 급여, 용역비]
DIRECT_CATS = ['급여', '용역비', '공구·자재비']   // 직접비
accIsDirect(cat) = DIRECT_CATS.includes(cat)
```

- **직접비**: 급여 · 용역비 · 공구·자재비
- **간접비**: 임대료 · 식대 · 세금 · 차량유지비 · 유류비 · 사무용품 · 기타

---

## 손익 계산

```
영업이익 = 매출(기준월 완결 청구) − 직접비 − 간접비
```

- 매출: `monthBill(pid, month)` — 완결(done) 대금청구서 합
- 월 비용: `accMonthExp()` = 수동입력 expenses + `paymentAsExpense()`(완결 지급예정서)
- PJT별 손익표 + 공통비용(PJT 미지정) 별도 표시

---

## 두 서브탭

| 서브탭 | 함수 | 내용 |
|--------|------|------|
| 영업이익 현황 | `renderAccPnl` | 매출·직접비·간접비·영업이익, PJT별 손익 |
| 비용 장부 | `renderAccLedger` | 카테고리별 집계, 상세내역, 비용입력·급여배분 버튼 |

---

## 급여 PJT 비율배분 (N10-2)

비용장부의 "👥 급여 배분" 버튼으로, 급여명세서의 실지급액을 PJT별로 나눠 직접비(급여)에 반영.

**흐름:**
1. 근로자 선택 (`workers` 컬렉션, `loadSalWorkers`)
2. `salLoadMonths` — 그 직원의 발행된 명세서 월 목록 (`payslips/{wid}/months` getDocs, 최신순)
3. 월 선택 → `salLoadNet` — **netPay(실지급액)** 로드
4. 급여일 자동 계산 (`defaultPayDate`) — 기준월의 익월 말일, 주말이면 직전 평일(금). date 입력칸으로 공휴일 등 직접 수정 가능
5. PJT별 비율(%) 입력 → `salCalc` 실시간 금액 계산 (합계 100% 초과 차단)
6. `salSave` 저장

**저장 규칙:**
- id: `salary_{wid}_{기준월}_{pjt}`
- 저장 전 동일 직원·동일 기준월 `salaryDist` 항목 전체 삭제 후 재작성 (PJT 개수 감소 시 잔존 방지)
- `date` = 급여일, `baseMonth` = 급여일이 속한 월(회계 반영월), `cat:'급여'`
- 회계 반영월 = 급여일 월. 예: 5월 급여 → 익월 말일(6월 말) 지급 → **6월 회계** 반영

**표시:**
- 비용장부 상세내역에 "👥 급여배분" 태그
- 항목 클릭 → `salDelConfirm`(삭제 확인)

---

## 비용 입력 (수동)

- `accOpenForm` — 날짜·카테고리·거래처·금액·PJT·결제수단·비고
- 합계 → 공급가·부가세 역산(`accSplitVat`), 면세(`accZeroVat`)
- `accSave` / `accDel`
