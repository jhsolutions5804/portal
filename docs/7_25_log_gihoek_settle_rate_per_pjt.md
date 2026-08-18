# 7.25. 개발로그 — 지급예정서 공수연동 다중 프로젝트 시 프로젝트별 단가 개별 수정

> 작성: 춘식이(Claude) · 2026-08-18

---

## 요청

직전 세션(r8)에서 지급예정서 공수연동에 다중 프로젝트 합산 기능을 추가했는데, 단가가 전체 프로젝트에 공통 적용되는 하나뿐이었음. FAB·SUP처럼 프로젝트마다 기술인력 단가가 다를 수 있어 프로젝트별로 개별 수정 가능하게 해달라는 요청.

## 수정 (`gihoek/index.html`)

- `settleDraft.mandayRateOverride`(객체, pjtId→rate) 신규 — `newSettle()` 초기화에 추가
- `rateForPjt(pid)`: 프로젝트별 override가 있으면 그 값, 없으면 상단 공통 `mandayRate`(또는 `TEAM_RATE`)를 기본값으로 반환
- `setRateForPjt(pid, v)`: 표의 단가 입력 변경 시 override 저장, 표/합계 갱신
- `mandayRowsHtml()`: 2개 이상 프로젝트 선택 시 단가 칸을 `<span>` 대신 프로젝트별 편집 가능한 `<input>`으로 변경(`fmtMoney` 콤마 포맷 동일 적용)
- `setMandayCard()`: 상단 "기술인력 단가" 라벨에 "기본값(신규 프로젝트 추가 시 사용) — 프로젝트별로 개별 수정 가능" 안내 문구 추가, 하단 합계 텍스트에도 프로젝트별 적용 단가(`공수 × 단가`) 표기
- `setSupply()`, `settleLines()`: 다중 프로젝트 시 공급가액·항목별 금액 계산에 공통 `mandayRate` 대신 `rateForPjt(pid)` 사용
- `fetchManday()`는 그대로 두어, 재조회 시 공수(`mandayOverride`)만 새로 받아온 값으로 리셋되고 단가 개별설정(`mandayRateOverride`)은 보존됨 — 공수만 갱신하고 싶을 때 단가를 매번 다시 칠 필요 없음

## 검증

- Node.js로 계산 시뮬레이션: FAB 120.0공수×190,000원 + SUP 62.6공수×210,000원(개별단가 적용) = 35,946,000원 정확히 산출 확인
- `node --check`로 `gihoek/index.html` 유일한 `<script type="module">` 블록 문법 검증 통과

## 배포

- `gihoek/index.html` (5.3.15 → 5.3.16)
- 루트 `index.html` 버전배너 갱신 (build 20260818g)
- 백업: `backup/v5.3.16/gihoek/index.html`
- 문서: `docs/1_4_gihoek_settle.md` r9 갱신
- 프로덕션 직접 배포
