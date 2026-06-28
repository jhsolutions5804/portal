# 2.3. 인사 — 연봉계약서

> Firestore 컬렉션: `annual_contracts/{workerId}/contracts/{yyyymmdd}`
> 최초 작성: 2026-06-27 · 작성: 춘식이(Claude)

---

## 업무 흐름상 위치

```
근로자 명부 등록
  └→ 근로계약서 작성 (시급 입력 → 계약연봉 자동 계산)
        └→ 연봉계약서 작성  ← 현재 문서
              └→ 급여명세서 작성 (연봉계약서 지급내역 자동 연동)
```

> ⚠️ **근로계약서를 먼저 작성해야** 연봉계약서에서 시급이 자동 연동된다.

---

## Firestore 스키마

```js
annual_contracts/{workerId}/contracts/{yyyymmdd}:
{
  name,          // 근로자명
  jumin,         // 주민번호 13자리
  dept,          // 소속
  rank,          // 직급
  empType,       // 'field' | 'office'
  hourly,        // 시급 (근로계약서 연동)
  basic,         // 기본급
  fixedOt,       // 고정연장수당 (사무직)
  fixedNight,    // 고정야간수당 (현장직)
  weekly,        // 주휴수당
  annual,        // 계약연봉 합계
  startDate,     // 계약 시작일
  endDate,       // 계약 종료일
  contractDate,  // 작성일
  signData,      // 근로자 서명 base64
  savedAt
}
```

---

## 급여 구성 계산 공식

시급(`hourly`)을 기반으로 직종에 따라 자동 계산된다.

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

---

## 화면 구성 (PC 테이블)

탭 진입 즉시 근로자 전체 목록을 테이블로 표시.

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
renderAnnualMain()  ← 탭 진입, PC 테이블
  ├─ 이름 클릭 or 조회 버튼 → annualViewWorker(wid, wname)
  │     ├─ 계약서 카드 목록 (계약일·기간·연봉·PDF출력·삭제)
  │     ├─ ← 목록 버튼 → renderAnnualMain()
  │     └─ ➕ 신규 작성 → annualRegisterForWorker(wid)
  └─ ➕ 신규 작성 버튼 → renderAnnualRegister()
        └─ ← 뒤로가기 → renderAnnualMain()
```

---

## 갑 서명/도장

- A4 출력 시 (갑) 김종화 옆에 `company_settings/signatures.kjh` 이미지 자동 삽입
- `loadCompSignatures()` 호출로 이미지 로드

---

## 급여명세서 연동

연봉계약서의 지급 항목이 급여명세서 작성 시 자동으로 연동된다.

| 연봉계약서 필드 | 급여명세서 항목 |
|----------------|----------------|
| `basic` | 기본급 |
| `fixedOt` | 고정연장수당 |
| `fixedNight` | 고정야간수당 |
| `weekly` | 주휴수당 |

- 연동 함수: `psWorkerSelect(wid)` — 근로자 선택 시 최신 연봉계약서 자동 로드
- ⚠️ 연봉계약서가 없으면 급여명세서 지급내역 자동 채움 불가

---

## 주의사항

1. **근로계약서 먼저** 작성 → 시급 자동 연동
2. **급여명세서 작성 전** 연봉계약서 반드시 존재해야 지급내역 자동 연동됨
3. A4 출력 시 `<\/script>` 이스케이프 필수

---

## 주요 함수

| 함수 | 역할 |
|------|------|
| `renderAnnualMain()` | PC 테이블 목록 (탭 진입점) |
| `annualViewWorker(wid, wname)` | 특정 근로자 계약서 상세 |
| `annualRegisterForWorker(wid)` | 해당 근로자로 신규 작성 폼 진입 |
| `renderAnnualRegister()` | 신규 작성 폼 (근로자 선택부터) |
| `annualWorkerSelect(wid)` | 근로자 선택 시 정보 + 시급 자동 채움 |
| `annualCalcSalary()` | 시급 → 급여 구성 실시간 계산 |
| `annualPreview()` | A4 PDF 새창 |
| `annualSave()` | Firestore 저장 |
| `annualDeleteContract(wid, cid, wname)` | 계약서 삭제 |
| `annualPreviewSaved(d)` | 저장된 계약서 PDF 출력 |
