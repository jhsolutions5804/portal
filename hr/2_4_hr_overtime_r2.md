# 2.4. 인사 — 초과근로

> Firestore 컬렉션: `overtime/{auto-id}`
> 최초 작성: 2026-06-26 · 최종 수정: 2026-06-27 · 작성: 춘식이(Claude)

---

## Firestore 스키마

```js
{ name, rank, yearMonth, date, hours, amount, rate, workerId, savedAt }
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

## PC 레이아웃 (r2, 2026-06-27)

`window.innerWidth >= 900` 기준으로 PC/모바일 자동 분기.

### PC 뷰 구성

```
┌─────────────────────────────────────────────────────────┐
│  ⏱ 초과근로          ◀ 2026년 06월 ▶                    │  ← 헤더
├──────────┬──────────┬──────────┬──────────────────────────┤
│ 총 시간  │ 총 수당  │  인원   │  건수                    │  ← KPI 바
├──────────┴──────────┴──────────┴──────────────────────────┤
│ 직원 목록  │                                              │
│ ─────────  │  (선택 직원) 상세 내역                      │
│ 홍길동 대리│  · 통상임금 정보                            │
│ 김철수 사원│  · 누계 시간 / 누계 수당 KPI               │
│ 이영희 과장│  · 날짜별 상세 테이블 (수정·삭제)          │
│           │                                              │
│ ─────────  │                                              │
│ ➕ 입력폼 │                                              │
│ 날짜      │                                              │
│ 직원 선택 │                                              │
│ 통상임금  │                                              │
│ 시간(h)   │                                              │
│ 예상수당  │                                              │
│ [저장]    │                                              │
│ [🗑초기화]│                                              │
└───────────┴──────────────────────────────────────────────┘
```

### 주요 함수

| 함수 | 역할 |
|------|------|
| `renderOvertimeMain()` | PC/모바일 분기 진입점 |
| `renderOvertimePC()` | PC 뷰 뼈대 렌더 + `otPcInit()` 호출 |
| `renderOvertimeMobile()` | 기존 모바일 카드 뷰 (변경 없음) |
| `otPcInit()` | 직원 목록 + select 초기화 + KPI 로드 |
| `otPcLoadKpiAndHours(workers)` | 월별 KPI 집계 + 직원별 시간 업데이트 |
| `otPcChangeMonth(delta)` | 월 변경 → KPI + 우패널 갱신 |
| `otPcSelectWorker(id, name, rank)` | 직원 클릭 → active 처리 + select 동기화 + 우패널 갱신 |
| `otPcShowPersonDetail(id, name, rank)` | 우패널: 통상임금·누계·날짜별 상세 |
| `otPcCalcPreview()` | 입력폼 통상임금 미리보기 |
| `otPcSave()` | 저장 후 KPI·우패널 갱신 |
| `otPcDelete(docId, ...)` | 삭제 후 KPI·우패널 갱신 |
| `otPcEdit(docId, ...)` | `renderOvertimeEdit(... 'pc')` 호출 |
| `otUpdate(docId, backType)` | `backType==='pc'` 분기 추가 — 저장 후 `renderOvertimeMain()` |

### 직원 선택 ↔ 입력폼 select 동기화

- 직원 목록 클릭 → `otPcSelectWorker()` → select도 해당 직원으로 동기화
- 입력폼 select 변경 → `otPcCalcPreview()` → 직원 목록 active도 동기화

---

## 급여명세서 연동

- 연동 항목: 급여명세서의 **상여금** 항목
- 조건: `overtime.name == 근로자명` AND `overtime.yearMonth == 기준월`
- ⚠️ 기준월 먼저 선택 후 연동됨
