# 1.0. 기획 홈

> `portal/gihoek/index.html` · URL: `.../portal/gihoek/?via=portal`
> 최초 작성: 2026-06-26 · 최종 수정: 2026-06-29 · 작성: 춘식이(Claude)

---

## UI 구조

- **헤더**: 탭 메뉴만 표시 (`.head > .tabs`)
  - 앱 자체 타이틀(📊 기획) 헤더 제거 — 포털 상단에 이미 표시되므로 중복
- **탭**: 홈 / 프로젝트 / 거래처 / 견적 / 정산 / 회계

---

## KPI 카드 구성

| 카드 | 데이터 소스 | 클릭 동작 |
|------|------------|---------|
| 진행 프로젝트 수 | `gihoek_projects` (status=run) | `planShowList('projects')` |
| 유효 견적 합계 | `gihoek_estimates` (status=active) | `planShowList('estimates')` |
| 대금 청구 누계 | `gihoek_settlements` (invoice, !void) | `planShowList('invoices')` |
| 미수 잔금 | 청구 누계 − **완결된 청구** 합계 | `planShowList('dues')` |

### 미수금 정의 (2026-06-26 재정의)
```
미수금 = pjtBilled(전체) − pjtDone(완결된 invoice 합계)
```
- 헬퍼: `pjtDone(pid)` — 완결(done) 청구서 합계
- 헬퍼: `pjtDue(pid)` — 프로젝트별 미수금

---

## KPI 팝업 (`planShowList`)

- 카드 클릭 시 모달 팝업으로 목록 표시
- 행 클릭 → 해당 탭·상세로 이동

---

## 바로가기 버튼

기획 홈 하단에 5개 탭으로 이동하는 바로가기 버튼 표시:

| 버튼 | 이동 탭 | 함수 |
|------|--------|------|
| 📁 프로젝트 | `pjt` | `tab('pjt')` |
| 🏢 거래처 | `comp` | `tab('comp')` |
| 📄 견적 | `est` | `tab('est')` |
| 💳 정산 | `settle` | `tab('settle')` |
| 📊 회계 | `acct` | `tab('acct')` |

### 뒤로가기 (2026-06-26 추가)
- 바로가기로 진입한 각 탭 최상단에 `← 기획 홈` 버튼 표시
- 클릭 시 `tab('home')` 호출 → 기획 홈으로 복귀
- 적용 탭: 프로젝트·거래처·견적·정산·회계 (5개 전체)
- 사용 스타일: 기존 `.back` CSS 클래스 그대로 활용

---

## onSnapshot 구독

홈 탭에서 3개 컬렉션 실시간 구독:
- `gihoek_projects` → KPI 갱신
- `gihoek_estimates` → KPI 갱신
- `gihoek_settlements` → KPI 갱신

> ⚠️ 각 구독에서 `curTab==='home'` 체크 후 `renderPlanHome()` 재호출 필요
