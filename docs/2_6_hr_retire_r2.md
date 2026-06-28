# 2.6. 인사 — 퇴직금 정산

> 현재 상태: PC/모바일 분기 레이아웃 구현, 자동 계산 기능 포함
> 최초 작성: 2026-06-26 · 최종 수정: 2026-06-29(r2) · 작성: 춘식이(Claude)

---

## 레이아웃 구조 (PC / 모바일 분기)

`window.innerWidth >= 900` 기준으로 분기

### PC 뷰 (`renderRetirePC`)
- `max-width:1100px; margin:0 auto` 스크롤 방식
- **좌측 280px 패널**
  - 산정 조건 (근로자 select + 퇴직일 date)
  - 📂 정산 내역 목록 (`#rt-list-panel`) — 근로자 선택 시 자동 로드
  - 주의문구 (참고용 안내)
- **우측 flex:1 패널** (`#rt-result`)
  - 근로자·퇴직일 선택 즉시 계산 결과 표시
  - 상단 요약 (이름·재직기간·예상 퇴직금)
  - 2열 그리드: 좌(① 평균임금 테이블) / 우(② 재직기간 + ③ 산식 + 퇴직금 배너 + 저장 버튼)
- 저장 후: 좌측 `#rt-list-panel`만 새로고침 (페이지 전환 없음)

### 모바일 뷰 (`renderRetireMobile`)
- 기존 카드 UI 그대로 유지
- 메뉴 선택 → `renderRetireCalcMobile()` / `renderRetireList()`

---

## 계산 공식

**퇴직금 = 적용 1일 평균임금 × 30일 × (재직일수 / 365)**

- 1일 평균임금 = 퇴직 전 3개월 임금 총액 ÷ 기간 일수
  - 포함 항목: 기본급 + 고정연장 + 고정야간 + 주휴 + 상여금
  - 제외 항목: 특별성과급, 특근수당
- 평균임금 < 통상임금 시 통상임금(1일 = 통상시급 × 8h) 적용
- 계속근로 1년 미만 → 0원

---

## 주요 함수

| 함수 | 역할 |
|------|------|
| `renderRetireMain()` | PC/모바일 분기 진입점 |
| `renderRetirePC()` | PC 뷰 뼈대 렌더 + 근로자 목록 로드 |
| `renderRetireMobile()` | 모바일 메인 카드 렌더 |
| `renderRetireCalcMobile()` | 모바일 산정 화면 (구 `renderRetireCalc` alias 유지) |
| `retireCompute()` | PC/모바일 공용 계산 로직 (분기 후 결과 렌더) |
| `rtLoadListPanel(wid, panel)` | PC 좌측 정산 내역 패널 로드 |
| `rtDeleteFromPanel(wid, rid)` | PC 패널 내 삭제 후 패널 갱신 |
| `retireSave()` | Firestore `severance/{wid}/records` 저장 |
| `renderRetireList()` | 모바일 전용 내역 조회 |
| `retireViewWorker(wid, wname)` | 모바일 근로자별 내역 보기 |
| `retireDelete(wid, rid, wname)` | 모바일 내역 삭제 |

---

## ⚠️ calcWorkDays 함수 위치 주의

`calcWorkDays` 함수와 `KR_HOLIDAYS` 상수는 **hr/index.html의 명부 섹션(근로자 명부) 내부**에 위치한다.

```
// hr/index.html 코드 구조
// 👥 근로자 명부 섹션
  const KR_HOLIDAYS = new Set([...]);   ← 여기
  function calcWorkDays(...) { ... }    ← 여기
  window.rosterDetail = ...
  ...
// 📝 근로계약서 섹션
```

**교체 시 체크리스트**
- 명부 섹션 코드 교체 시 `KR_HOLIDAYS` + `calcWorkDays`를 새 코드에도 반드시 포함
- 누락 시: 퇴직금 탭 계산 오류 + 명부 상세 모달 재직기간 0 표시

> 실제 사고(2026-06-27): 명부 코드 교체 시 두 함수 누락 → `fix` 커밋으로 복원
