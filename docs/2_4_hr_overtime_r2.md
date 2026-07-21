# 2.4. 인사 — 초과근로

> Firestore 컬렉션: `overtime/{auto-id}`
> 최초 작성: 2026-06-26 · 최종 수정: 2026-07-21(r3) · 작성: 춘식이(Claude)

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

## 급여명세서 연동

- 연동 항목: 급여명세서의 **상여금** 항목
- 조건: `overtime.name == 근로자명` AND `overtime.yearMonth == 기준월`
- ⚠️ 기준월 먼저 선택 후 연동됨


---

## 전자결재 초과근로 승인 자동 연동 (2026-07-06, v2.1.0 / 2026-07-21 reason 필드 추가)

전자결재 초과근로(`edoc_overtime`)가 **승인되면** 이 `overtime` 컬렉션에 자동 등록된다. (PC·모바일 공통)

- 트리거: `docApprove`/`mobileApprove`에서 `newStatus==='approved' && dtype==='overtime' && !linkedToOvertime`
- 등록 필드: `{ date, name, rank, workerId, hours, amount, rate, reason, yearMonth, savedAt }`
- 중복 방지: `edoc_overtime` 문서에 `linkedToOvertime:true` 플래그
- 통상임금 rate·수당 amount는 전자결재 작성 시 통상임금 계산으로 이미 확정(→ `3_4_edoc_overtime` 참조)
- 사유(`reason`)는 전자결재 상신 폼에서 입력한 값이 그대로 복사된다.

