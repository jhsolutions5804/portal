# 2.5. 인사 — 급여명세서

> Firestore 컬렉션: `payslips/{workerId}/months/{yyyy-mm}`
> 최초 작성: 2026-06-26 · 최종 수정: 2026-06-27 · 작성: 춘식이(Claude)

---

## Firestore 스키마

```js
{
  month, payDate, bankAccount, hourly, empType,
  basic, fixedOt, fixedNight, weekly,       // 연봉계약서 연동
  bonus, specialBonus, extraPay,            // 직접 입력
  grossPay, pension, health, ltcare, employ,
  dormitory, incomeTax, localTax, totalDeduct, netPay, savedAt
}
```

---

## 공제 계산 (`psCalcAll`)

```
국민연금     = 지급계 × 4.5%
건강보험     = 지급계 × 3.545%
장기요양보험 = 건강보험 × 12.81%
고용보험     = 지급계 × 0.9%
소득세       = 간이세액표 (부양가족 1인 기준)
지방소득세   = 소득세 × 10%
```

**간이세액표 근사치**
```
≤ 1,060,000 → 0원
≤ 1,500,000 → 지급계 × 0.6%
≤ 3,000,000 → 지급계 × 1.0%
≤ 4,500,000 → 지급계 × 15% - 420,000
≤ 7,800,000 → 지급계 × 24% - 825,000
초과         → 지급계 × 35% - 1,680,000
```

---

## 주의사항

1. **연봉계약서 먼저** → 급여명세서에서 지급내역 연동
2. **기숙사 공제**: `onchange` 사용 (oninput 사용 시 오류)
3. **지급일**: 기준월 선택 시 익월 말일 자동설정, 수동 수정 가능

---

## 주요 함수

| 함수 | 역할 |
|------|------|
| `renderPayslipWrite()` | 작성 폼 |
| `psWorkerSelect(wid)` | 계좌 + 연봉계약서 지급내역 로드 |
| `psCalcAll()` | 전체 지급/공제/실지급액 계산 |
| `calcPayDateGlobal(month)` | 기준월 → 익월 말일 |
