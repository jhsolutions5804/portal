# 2.4. 인사 — 초과근로

> Firestore 컬렉션: `overtime/{auto-id}`
> 최초 작성: 2026-06-26 · 최종 수정: 2026-08-27(v1.0.1, 누계/총 수당 금액 표시 정정) · 작성: 춘식이(Claude)

---

## Firestore 스키마

```js
{ name, rank, yearMonth, date, hours, amount, rate, reason, workerId, savedAt }
```

> ⚠️ **r3 정정**: 과거(r2) 문서에는 인사 직접입력분이 `pay`·`hourlyWage` 필드를 쓴다고 기록되어 있었으나, 현재 `hr/index.html` 코드는 PC·모바일 모두 `amount`·`rate` 필드로 통일되어 있다(전자결재 자동연동분과 동일). `pay`·`hourlyWage`는 더 이상 사용되지 않는다.
> `reason`(사유)은 2026-07-21 추가된 필드다. 선택 입력이며 값이 없으면 화면에 "-"로 표시된다. 기존 데이터는 마이그레이션 없이 그대로 호환된다.

---

## 입력 규칙

| 항목 | 규칙 |
|------|------|
| 날짜 | YYYY-MM-DD, date picker |
| 직원 | workers 컬렉션 연동 드롭다운 |
| 시간 | 0.5h 단위, 최소 0.5h ~ 최대 24h |
| 수당 | 직접 입력 불가 — 통상임금 × 시간 자동 계산 |
| 사유 | 텍스트영역, 선택 입력 (필수 아님) |
| 중복 | 동일 날짜·직원 → 별도 문서 저장 (합산됨) |

**통상임금 = (기본 + 고정연장 + 고정야간 + 주휴) ÷ 209**

---

## 클릭 상세보기 모달 (2026-07-26)

목록/조회 화면의 사유 컬럼은 공간 제약상 말줄임(ellipsis) 처리되어 긴 사유가 잘려 보이는 문제가 있었음. 세 테이블(PC 직원 상세 `otPcShowPersonDetail`, 모바일 직원별 조회 `otLoadPersonDetail`, 전체현황 날짜별 상세 `otLoadSummary`) 모두 행 클릭 시 `window.otShowDetail(rowId)`가 이름·날짜·시간·수당과 **사유 전문**을 모달로 보여준다.

- 각 렌더 함수가 행을 그릴 때 `_otDetailCache[r.id] = r`로 원본 데이터를 캐시하고, `<tr onclick="otShowDetail('${r.id}')">`로 연결
- 수정·삭제 버튼은 `event.stopPropagation()`으로 모달이 뜨지 않도록 분리
- 모달은 배경 클릭 또는 ✕ 버튼으로 닫힘, 사유는 `white-space:pre-wrap`으로 줄바꿈 유지

---

## 급여명세서 연동

- 연동 항목: 급여명세서의 **상여금** 항목
- 조건: `overtime.name == 근로자명` AND `overtime.yearMonth == 기준월`
- ⚠️ 기준월 먼저 선택 후 연동됨


---

## 전자결재 초과근로 승인 자동 연동 (2026-07-06, v2.1.0 / 2026-07-21 reason 필드 추가 / 2026-07-24 self-heal 추가)

전자결재 초과근로(`edoc_overtime`)가 **승인되면** 이 `overtime` 컬렉션에 자동 등록된다. (PC·모바일 공통)

- 트리거: `docApprove`/`mobileApprove`에서 `newStatus==='approved' && dtype==='overtime' && !linkedToOvertime`
- 등록 필드: `{ date, name, rank, workerId, hours, amount, rate, reason, yearMonth, savedAt }`
- 중복 방지: `edoc_overtime` 문서에 `linkedToOvertime:true` 플래그
- 통상임금 rate·수당 amount는 전자결재 작성 시 통상임금 계산으로 이미 확정(→ `3_4_edoc_overtime` 참조)
- 사유(`reason`)는 전자결재 상신 폼에서 입력한 값이 그대로 복사된다.

### 자동 재동기화(self-heal) — `window.otSyncFromEdoc()` (2026-07-24)

`docApprove()`의 즉시연동이 실패하거나 누락되는 경우(원인 미상 사례 발생, `3_4_edoc_overtime` 참조)를 대비해,
**인사 → 초과근로 탭에 진입할 때마다** 자동으로 아래를 수행한다.

1. `edoc_overtime`에서 `status==='approved' && !linkedToOvertime`인 문서를 전부 조회
2. 있으면 `overtime`에 추가 + 해당 `edoc_overtime` 문서에 `linkedToOvertime:true` 마킹
3. 없으면 아무 동작 안 함 (매번 호출돼도 idempotent, 중복 등록 없음)

별도 조작·스크립트 실행 없이 인사 앱의 초과근로 탭을 여는 것만으로 누락 건이 자동 복구된다.



---

## 금액 표시 정정 (2026-08-27, v1.0.1)

PC 화면의 "누계 수당"(개별 직원 상세 패널, `otPcShowPersonDetail`)과 "총 수당"(상단 KPI, `otPcLoadKpiAndHours`) 표시가 10,000원 이상일 때 `Math.round(v/10000)+'만원'`으로 반올림되어 정확한 금액이 아닌 근사치(예: 128,730원 → 13만원)로 보이는 문제가 있었음. 포털 전체 UI 컨벤션(금액은 항상 1,000단위 콤마 표시)에 맞춰 두 곳 모두 `v.toLocaleString()+'원'`으로 수정, 1원 단위까지 정확히 표시하도록 변경.

- 모바일 뷰(`otLoadPersonDetail` 등)는 원래부터 `toLocaleString()` 방식이라 영향 없었음
- 영향 함수: `otPcLoadKpiAndHours`(총 수당 KPI), `otPcShowPersonDetail`(개별 직원 누계 수당)
