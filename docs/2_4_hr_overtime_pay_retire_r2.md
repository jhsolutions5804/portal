# 2.4. 인사 — 초과근로

> Firestore 컬렉션: `overtime/{auto-id}`
> 최초 작성: 2026-06-26 · 최종 수정: 2026-06-27 · 작성: 춘식이(Claude)

---

## Firestore 스키마

```js
{ name, yearMonth, date, hours, pay, workerId, hourlyWage, savedAt }
```

---

## 입력 규칙

| 항목 | 규칙 |
|------|------|
| 날짜 | YYYY-MM-DD, date picker |
| 직원 | workers 컬렉션 연동 드롭다운 |
| 시간 | 0.5h 단위, 최소 0.5h ~ 최대 24h |
| 수당 | 직접 입력 불가 — 통상임금 × 시간 자동 계산 |
| 중복 | 동일 날짜·직원 → 별도 문서 저장 (합산됨) |

**통상임금 = (기본 + 고정연장 + 고정야간 + 주휴) ÷ 209**

---

## 급여명세서 연동

- 연동 항목: 급여명세서의 **상여금** 항목
- 조건: `overtime.name == 근로자명` AND `overtime.yearMonth == 기준월`
- ⚠️ 기준월 먼저 선택 후 연동됨

---

# 2.5. 인사 — 급여명세서

> Firestore 컬렉션: `payslips/{workerId}/months/{yyyy-mm}`

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

---

# 2.6. 인사 — 퇴직금 정산

> 현재 상태: 탭 구현, 자동 계산 기능 포함

**퇴직금 = 1일 평균임금 × 30일 × (재직일수 / 365)**
- 재직일수: `calcWorkDays(startStr, endStr)` — 주말·공휴일 제외
- 3개월 평균임금 기준 산정

---

## ⚠️ calcWorkDays 함수 위치 주의

`calcWorkDays` 함수와 `KR_HOLIDAYS` 상수는 **hr/index.html의 명부 섹션(근로자 명부) 내부**에 위치한다.

```
// hr/index.html 코드 구조
// 👥 근로자 명부 섹션
  const KR_HOLIDAYS = new Set([...]);   ← 여기
  function calcWorkDays(...) { ... }    ← 여기
  window.rosterDetail = ...
  ...
// 📝 근로계약서 섹션
```

**교체 시 체크리스트**
- 명부 섹션 코드 교체 시 `KR_HOLIDAYS` + `calcWorkDays`를 새 코드에도 반드시 포함
- 누락 시: 퇴직금 탭 계산 오류 + 명부 상세 모달 재직기간 0 표시

> 실제 사고(2026-06-27): 명부 코드 교체 시 두 함수 누락 → `fix` 커밋으로 복원
