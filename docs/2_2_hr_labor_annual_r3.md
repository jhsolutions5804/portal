# 2.2. 인사 — 근로계약서

> Firestore 컬렉션: `labor_contracts/{workerId}/contracts/{yyyymmdd}`
> 최초 작성: 2026-06-26 · 최종 수정: 2026-06-27 · 작성: 춘식이(Claude)

> ℹ️ **연봉계약서(2.3)는 `2_3_hr_annual.md`로 분리됨** (2026-06-27)

---

## 화면 구성 (D3 기준 — PC 테이블)

탭 진입 즉시 근로자 전체 목록을 테이블로 표시 (근로자 명부 v3와 동일 패턴).

**컬럼**: 사원번호 · 이름 · 소속 · 직급 · 구분 · 최신 계약일 · 계약 수 · 상태 · 조회

| 컬럼 | 설명 |
|------|------|
| 사원번호 | empNo |
| 이름 | 클릭 시 계약서 상세로 이동 |
| 소속 | dept |
| 직급 | rank |
| 구분 | 현장(노랑) / 사무(파랑) 배지 |
| 최신 계약일 | 가장 최근 contractDate |
| 계약 수 | 전체 계약서 건수 |
| 상태 | ✅ 유효 / ⚠️ 만료 / 미작성 |
| 조회 | 상세 버튼 |

**상태 컬러**
- 유효: `#16A34A` 초록
- 만료: `#DC2626` 빨강
- 미작성/없음: `#9AAABF` 회색

---

## 탭 흐름

```
renderLaborMain()  ← 탭 진입, PC 테이블
  ├─ 이름 클릭 or 조회 버튼 → laborViewWorker2(wid, wname)
  │     ├─ 계약서 카드 목록 (계약일·기간·연봉·PDF출력·삭제)
  │     ├─ ← 목록 버튼 → renderLaborMain()
  │     └─ ➕ 신규 작성 → laborRegisterForWorker(wid) → 해당 근로자 자동 선택
  └─ ➕ 신규 작성 버튼 → renderLaborRegister()
        └─ ← 뒤로가기 → renderLaborMain()
```

---

## Firestore 스키마

```js
labor_contracts/{workerId}/contracts/{yyyymmdd}:
{
  name, jumin, phone, address, dept, rank, job,
  empType,    // 'field' | 'office'
  hourly,     // 시급
  salary,     // 계약연봉 (자동 계산)
  startDate, endDate, contractDate,
  signData,   // 서명 base64
  savedAt
}
```

---

## 급여 계산 공식 (`calcAnnualSalary`)

**현장직 (field)**
```
basic      = hourly × 8 × 5 × 4.345
fixedNight = hourly × 0.5 × 8 × 5 × 4.345
weekly     = hourly × 8 × 4.345
annual     = (basic + fixedNight + weekly) × 12
```

**사무직 (office)**
```
basic    = hourly × 8 × 5 × 4.345
fixedOt  = hourly × 12 × 4.345
weekly   = hourly × 8 × 4.345
annual   = (basic + fixedOt + weekly) × 12
```

> ℹ️ 동일 공식이 연봉계약서(`2_3_hr_annual.md`)에도 적용됨.

---

## 갑 서명/도장 (B4)

- A4 출력 시 (갑) 김종화 옆에 `company_settings/signatures.kjh` 이미지 자동 삽입
- `loadCompSignatures()` 호출로 이미지 로드

---

## 주의사항

1. **근로계약서 먼저** 작성 → 연봉계약서에서 시급 자동 연동
2. `renderLaborForm` 전역 등록 필수 (`window.laborRefreshForm2`)
3. A4 출력 시 `<\/script>` 이스케이프 필수

---

## 주요 함수

| 함수 | 역할 |
|------|------|
| `renderLaborMain()` | PC 테이블 목록 (탭 진입점) |
| `laborViewWorker2(wid, wname)` | 특정 근로자 계약서 상세 |
| `laborRegisterForWorker(wid)` | 해당 근로자로 신규 작성 폼 진입 |
| `renderLaborRegister()` | 신규 작성 폼 (근로자 선택부터) |
| `laborWorkerSelect2(wid)` | 근로자 선택 시 정보 자동 채움 |
| `laborUpdateSalaryPreview()` | 시급 → 급여구성 실시간 표시 |
| `laborPreview2()` | A4 PDF 새창 |
| `laborSave2()` | Firestore 저장 |
| `laborDeleteContract2(wid,cid,wname)` | 계약서 삭제 |
| `laborPreviewSaved2(d)` | 저장된 계약서 PDF 출력 |
