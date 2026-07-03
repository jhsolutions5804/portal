# 2.0. 인사 홈

> `portal/hr/index.html` · URL: `.../portal/hr/?via=portal`
> 최초 작성: 2026-06-26 · 최종 수정: 2026-07-03(r3a) · 정산도우미 가이드 대조 후 PDF 출력 규격 보완 · 작성: 춘식이(Claude)

---

## 접근 방식 (포털 전용)

- `?via=portal` 파라미터 없이 직접 URL 접근 시 차단 화면 표시
- Firebase Auth 완전 제거 (Firestore 데이터 R/W용으로만 유지)
- 권한 부여는 오직 `portal/index.html`에서 담당

---

## 레이아웃 구조

- **내부 사이드바 없음** (제거됨)
- PC: `app-header` · 탭바 숨김 → 콘텐츠 풀너비
- 모바일: 상단 `app-header` + 수평 스크롤 탭바

---

## 탭 구성 및 PC 레이아웃

| 탭 | PC 레이아웃 |
|----|------------|
| 인사 홈 | KPI 카드 + 업무흐름 카드 |
| 근로자 명부 | 탭 진입 즉시 PC 테이블 (`max-width:1100px`) |
| 근로계약서 | 탭 진입 즉시 PC 테이블 |
| 연봉계약서 | 탭 진입 즉시 PC 테이블 |
| 초과근로 | PC/모바일 분기 (`window.innerWidth >= 900`) |
| 급여명세서 | PC/모바일 분기 (`PS_PC_BP = 900`) |
| 퇴직금 정산 | PC/모바일 분기 |
| 연차 현황 | 풀너비 테이블 |

---

## 인사 홈 버튼 (homeBtn)

각 탭 메인 화면 좌측 상단 `🏠 인사 홈` 버튼 — 7개 탭 전체 적용.
동작: `goTab('home')` 호출.

```js
const homeBtn = () =>
  `<button onclick="goTab('home')" style="background:#F0F4F9;border:1px solid #DDE4EF;
   border-radius:8px;padding:5px 12px;color:#5C6F8A;font-size:12px;cursor:pointer;
   font-weight:600;">🏠 인사 홈</button>`;
```

---

## KPI 카드

| 카드 | 데이터 소스 | 클릭 |
|------|------------|------|
| 전체 직원 | `workers` 전체 | `hrShowList('workers')` |
| 이번 달 급여 합계 | `payslips` (이번 달) | `hrShowList('payslips')` |
| 초과근로 수당 | `overtime` (이번 달) | `hrShowList('overtime')` |
| 연차 잔여 평균 | `workers` + `edoc_leave` | `hrShowList('leaves')` |

---

## 서명/도장 관리 (관리자 전용)

- **저장**: `company_settings/signatures.kjh` — base64 이미지
- **출력 반영**: 근로계약서·연봉계약서 A4 출력 시 자동 삽입
- **함수**: `loadCompSignatures`, `saveCompSignature`, `renderSignMgr`

---

## PDF 출력 규격 (급여명세서·근로/연봉계약서 공통)

| 구분 | 규격 |
|------|------|
| 용지 | A4 (210mm × 297mm) |
| 여백 | 16mm 18mm |
| 폰트 | Malgun Gothic, Arial |
| 로고 | `JH_LOGO` (급여명세서 우상단) |
| 출력 | `window.print()` → PDF 저장 |

> 근로/연봉계약서는 `company_settings/signatures.kjh` 서명·도장이 A4 출력 시 자동 삽입됨(위 서명/도장 관리 참조).
> 출처: 구 정산도우미(`administrator`) 인사섹션 가이드 대조 결과, portal/hr 코드로 재검증하여 반영(2026-07-03). 나머지 항목(급여 공식·공제율·간이세액표·Firebase 스키마·Work Flow)은 이미 2.1~2.6 문서에 반영 완료.
