# 2.5. 인사 — 급여명세서

> Firestore 컬렉션: `payslips/{workerId}/months/{yyyy-mm}`
> 최초 작성: 2026-06-26 · 최종 수정: 2026-07-22(r5)-03(r4)-29(r3)-27(r2) · 작성: 춘식이(Claude)

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
2. **기숙사 공제**: `onchange` 사용 (oninput 사용 시 오류) — 상여금/특별상여/기타수당도 동일 원칙 적용(r5)
3. **지급일**: 기준월 선택 시 익월 말일 자동설정, 수동 수정 가능
4. **PC 레이아웃**: `tab-content`가 `display:block`이므로 `height:100%/flex:1` 방식 불가 → `max-width:1100px; margin:0 auto` 스크롤 방식 사용 (초과근로 동일 패턴)

---

## 공제내역 직접 수정 기능 (r3, 2026-06-29)

### 동작 방식
| 상황 | 동작 |
|------|------|
| 근로자/기준월 선택 | 공식 자동계산값으로 input 채움 |
| 직접 수정 | 입력값으로 공제계·실지급액 즉시 재계산 |
| 근로자 변경 | 수정값 초기화 → 새 자동계산값으로 리셋 |
| 조회/출력(PDF) | 저장 시점의 수정값 그대로 표시 |

### 관련 변수
- `ps._pension`, `ps._health`, `ps._ltcare`, `ps._employ`, `ps._incomeTax`, `ps._localTax`
- `undefined`이면 자동계산, 숫자면 오버라이드

### 저장 구조 (Firestore)
```
payslips/{workerId}/months/{month}
  pension, health, ltcare, employ, incomeTax, localTax  ← 실제 저장된 공제값
  totalDeduct, netPay  ← 저장 시점 기준
```

---

## 지급내역 직접 수정 기능 (r4, 2026-07-03)

공제내역(r3)과 동일한 오버라이드 방식으로, 지급내역의 연봉계약서 연동 항목(기본급·고정연장·고정야간·주휴)도 PC 화면에서 직접 수정 가능.

### 동작 방식
| 상황 | 동작 |
|------|------|
| 근로자/기준월 선택 | 연봉계약서 자동값으로 input 채움 |
| 직접 수정 | 입력값으로 지급계·공제(4대보험·소득세)·실지급액 즉시 재계산 |
| 근로자 변경/뷰 재진입 | 수정값 초기화 → 자동값 리셋 |
| 조회/출력(PDF) | 저장 시점 지급값 그대로 표시 |

### 관련 변수
- `ps._basic`, `ps._fixedOt`, `ps._fixedNight`, `ps._weekly` — `undefined`면 자동값, 숫자면 오버라이드
- `psCalcAll`에서 `sal` 구성 시 반영 → `sal.total`·`totalPay` 재계산 → 공제·실지급액 연쇄 갱신

### 범위
- **PC 전용**(`renderPayslipPCRight`). 모바일은 공제와 동일하게 표시 전용 유지
- 저장은 기존 `...c.sal` 스프레드로 자동 반영, 재출력 시 `ps._basic` 등 세팅으로 수정값 보존

---

## 입력 커서 초기화 버그 수정 (r5, 2026-07-22)

### 증상
PC 급여명세서 작성 화면에서 **상여금(초과근로)·특별상여·기타수당** 입력란에 숫자를 입력할 때, 한 글자 입력할 때마다 포커스가 풀려 매번 다시 클릭해야 입력이 가능한 현상.

### 원인
`renderPayslipPCRight()` 내 `inp()` 헬퍼 함수가 해당 3개 필드에 `oninput` 이벤트를 사용 → 키 입력마다 우패널 전체를 `innerHTML`로 재생성 → input DOM이 통째로 교체되며 포커스/커서 소실.

같은 화면의 기본급·국민연금 등 다른 입력란은 이미 `onchange`(포커스 이탈 시에만 반영)를 사용 중이라 문제가 없었음. 기숙사 공제 항목도 과거 동일한 이유로 `onchange`로 되어 있었음(위 주의사항 2번).

### 수정
`inp()` 헬퍼의 이벤트를 `oninput` → `onchange`로 통일. 타이핑 중에는 재렌더링 없이 자유롭게 입력하고, 필드에서 포커스를 벗어나면 지급계·공제계·실지급액이 갱신됨(기존 다른 필드와 동일 동작).

### 영향 범위
- PC 전용(`renderPayslipPCRight`)의 상여금/특별상여/기타수당 3개 필드
- 모바일 작성 폼(`renderPayslipWriteForm`)은 이미 `onchange` 사용 중이라 해당 없음

