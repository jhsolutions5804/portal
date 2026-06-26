# 2.5. 인사 — 급여명세서

> Firestore 컬렉션: `payslips/{workerId}/months/{yyyy-mm}`
> 최초 작성: 2026-06-26 · 최종 수정: 2026-06-27(r2) · 작성: 춘식이(Claude)

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

## PC 레이아웃 (`PS_PC_BP = 900`)

`window.innerWidth >= 900` 이면 PC 뷰, 미만이면 모바일 뷰로 분기.

### PC — 작성 (`renderPayslipPC`)

```
┌──────────────────────────────────────────────┐
│  💰 급여명세서                    📂 조회 목록 │  ← 헤더
├──────────────┬───────────────────────────────┤
│ 📋 기준 정보  │  💳 지급 내역  │ ➖ 공제 내역  │
│  ① 기준월    │  (연봉계약서   │  (4대보험·세금│
│  ② 근로자    │   연동 + 입력) │   + 기숙사)   │
│  지급일      ├───────────────┴───────────────┤
│             │  실 지급액 (파란 바)            │
│ 👤 근로자   │  📄 미리보기  /  ✅ 확정 저장   │
│   정보표시   │                               │
└──────────────┴───────────────────────────────┘
```

- 좌패널: 고정 260px, 기준월·근로자 select + 지급일 + 근로자 기본정보
- 우패널: `flex:1`, 지급/공제 **2열 grid**, 실지급액 바, 버튼
- 근로자 미선택 시 우패널에 안내 메시지

### PC — 조회 (`renderPayslipPCList`)

```
┌──────────────────────────────────────────────┐
│  📂 급여명세서 조회                   ✏️ 작성  │
├──────────────┬───────────────────────────────┤
│ 근로자 목록  │  카드 그리드 (auto-fill 220px) │
│  (클릭 시    │  ┌──────┐ ┌──────┐ ┌──────┐  │
│   우패널     │  │ 6월  │ │ 5월  │ │ 4월  │  │
│   갱신)      │  │ 실지급│ │ 실지급│ │ 실지급│  │
│              │  │PDF·삭│ │PDF·삭│ │PDF·삭│  │
│              │  └──────┘ └──────┘ └──────┘  │
└──────────────┴───────────────────────────────┘
```

- 좌패널: 240px, 근로자 목록 (선택 시 파란 강조)
- 우패널: 월별 명세서 카드 자동 그리드

### 모바일 — 기존 유지

`renderPayslipWrite` → `renderPayslipWriteForm` 카드 수직 스택 유지.

---

## 주요 함수

| 함수 | 역할 | 뷰 |
|------|------|----|
| `renderPayslipMain2()` | 진입점 — PC/모바일 분기 | 공통 |
| `renderPayslipPC()` | PC 작성 화면 뼈대 + 핸들러 등록 | PC |
| `renderPayslipPCRight()` | PC 우패널 계산값 렌더 (재호출 가능) | PC |
| `renderPayslipPCList()` | PC 조회 화면 | PC |
| `psLoadWorkerSlips(wid, wname, btn)` | PC 조회 우패널 로드 | PC |
| `psDeleteSlipPC(wid, mid, wname)` | PC 삭제 후 우패널 갱신 | PC |
| `psPcMonthChange(month)` | PC 기준월 변경 → 초과근로 재연동 | PC |
| `psPcWorkerSelect(wid)` | PC 근로자 선택 → 연봉계약서 로드 | PC |
| `renderPayslipWrite()` | 모바일 작성 폼 | 모바일 |
| `psWorkerSelect(wid)` | 모바일 근로자 선택 | 모바일 |
| `renderPayslipListNew()` | 모바일 조회 목록 | 모바일 |
| `psCalcAll()` | 전체 지급/공제/실지급액 계산 | 공통 |
| `calcPayDateGlobal(month)` | 기준월 → 익월 말일 | 공통 |
| `psPreview()` | PDF 미리보기 팝업 | 공통 |
| `psSave()` | Firestore 저장 | 공통 |
| `psViewDetail(d, wid)` | 저장 데이터로 PDF 미리보기 | 공통 |
| `psDeleteSlip(wid, mid, wname)` | 모바일 삭제 | 모바일 |

---

## 주의사항

1. **연봉계약서 먼저** → 급여명세서에서 지급내역 연동
2. **기숙사 공제**: `onchange` 사용 (oninput 사용 시 오류)
3. **지급일**: 기준월 선택 시 익월 말일 자동설정, 수동 수정 가능
4. **PC 레이아웃**: `tab-content`가 `display:block`이므로 `height:100%/flex:1` 방식 불가 → `max-width:1100px; margin:0 auto` 스크롤 방식 사용 (초과근로 동일 패턴)
