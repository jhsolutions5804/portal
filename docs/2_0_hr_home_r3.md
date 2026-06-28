# 2.0. 인사 홈

> `portal/hr/index.html` · URL: `.../portal/hr/?via=portal`
> 회사: 제이에이치솔루션 · 사업자번호: 383-09-02847
> 최초 작성: 2026-06-26 · 최종 수정: 2026-06-29 · 작성: 춘식이(Claude)

---

## 접근 방식 (D3, 2026-06-29)

- **포털 전용 접근** — `?via=portal` 파라미터 없이 직접 URL 접근 시 차단 화면 표시
- Firebase Auth 완전 제거 (Firestore 데이터 R/W용으로만 유지)
- 권한 부여는 오직 `portal/index.html`에서 담당
- 직접 접근 시: "포털을 통해 접근해주세요" 안내 카드 표시 (`blocked-screen`)

```js
// 인증 로직 요약
const viaPortal = new URLSearchParams(location.search).get('via') === 'portal';
if (viaPortal) {
  document.documentElement.classList.add('portal-embed');
  showScreen('app');
} else {
  showScreen('blocked');
}
```

---

## 레이아웃 구조

- **내부 사이드바 없음** (D1, 2026-06-29 제거)
- 포털 메인 사이드바가 내비게이션을 제공하므로 hr 앱 자체 사이드바 불필요
- PC: 상단 `app-header` 숨김 + 탭바 숨김 → 콘텐츠 풀너비 표시
- 모바일: 상단 `app-header` + 수평 스크롤 탭바 표시

---

## 탭 구성

| 탭 | 주요 기능 |
|----|---------|
| 인사 홈 | KPI 카드, 업무흐름 카드, 서명/도장 관리 |
| 근로자 명부 | workers 컬렉션 CRUD |
| 근로계약서 | 계약서 작성·PDF |
| 연봉계약서 | 연봉계약서 작성·PDF |
| 초과근로 | 초과근로수당 집계·관리 (PC/모바일 분기) |
| 급여명세서 | 월별 급여 계산·PDF |
| 퇴직금 정산 | 퇴직금 자동 계산 |
| 연차 현황 | 전체 직원 연차 부여·사용·잔여 조회 |

---

## 인사 홈 버튼 (G1, 2026-06-29)

각 탭 메인 화면 좌측 상단에 `🏠 인사 홈` 버튼 배치.

- **적용 탭**: 근로자 명부 · 근로계약서 · 연봉계약서 · 초과근로 · 급여명세서 · 퇴직금 정산 · 연차 현황 (7개 전체)
- **동작**: `goTab('home')` 호출
- **헬퍼 함수**: `homeBtn()` — `backBtn2()`와 동일 스타일, 회색 계열

```js
const homeBtn = () =>
  `<button onclick="goTab('home')" style="background:#F0F4F9;border:1px solid #DDE4EF;
   border-radius:8px;padding:5px 12px;color:#5C6F8A;font-size:12px;cursor:pointer;
   font-weight:600;">🏠 인사 홈</button>`;
```

---

## 업무흐름 카드

```
근로자 명부 등록
  └→ 근로계약서 작성 (시급 입력 → 계약연봉 자동 계산)
        └→ 연봉계약서 작성 (근로계약서 시급 자동 연동)
              └→ 급여명세서 작성 (연봉계약서 지급내역 자동 연동)
```

- 카드 배치: 1~8번 순서 (6·7번 나란히, 8번도 동일 행)

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

- **저장**: `company_settings/signatures` → `{ kjh: "data:image/..." }`
- **등록 UI**: 인사 홈 하단 "🖊️ 서명/도장 관리" 섹션
- **출력 반영**: 근로계약서·연봉계약서 A4 출력 시 (갑) 김종화 옆 자동 삽입
- **함수**: `loadCompSignatures`, `saveCompSignature`, `renderSignMgr`
