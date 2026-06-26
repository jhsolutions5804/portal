# 2.6. 인사 — 퇴직금 정산

> 현재 상태: 탭 구현, 자동 계산 기능 포함
> 최초 작성: 2026-06-26 · 최종 수정: 2026-06-27 · 작성: 춘식이(Claude)

---

## 계산 공식

**퇴직금 = 1일 평균임금 × 30일 × (재직일수 / 365)**

- 재직일수: `calcWorkDays(startStr, endStr)` — 주말·공휴일 제외
- 3개월 평균임금 기준 산정

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
