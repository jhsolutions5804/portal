# 7.23. 개발로그 — 지급예정서 공수연동 시 여러 프로젝트 합산 발행

> 작성: 춘식이(Claude) · 2026-08-18

---

## 요청

지급예정서를 "공수 연동" 방식으로 작성할 때, P4 Ph2(FAB)와 P4 Ph4(SUP)를 겸직하는 하청업체에 대해 지금까지는 프로젝트를 1개만 선택할 수 있어 정산서를 2개(Ph2용, Ph4용) 따로 발행해야 했음. 하나의 정산서에 합쳐서 발행할 수 있게 해달라는 요청.

## 설계

- 상단 "프로젝트" 단일 선택(`d.pjtId`)은 그대로 유지 — 대표 프로젝트로서 수신자 기본값·문서 목록의 대표 배지·필터 등에 계속 사용
- "공수 연동" 카드 안에 별도로 다중 선택 가능한 프로젝트 체크박스(`d.pjtIds`) 추가. 상단에서 고른 프로젝트는 항상 자동 포함되고, 필요한 만큼 추가로 체크
- 1개만 선택된 가장 흔한 경우는 기존 UI/저장 형식을 그대로 유지해 하위호환 보장. 2개 이상일 때만 프로젝트별 행으로 분리 렌더링

## 수정 내역 (`gihoek/index.html`)

- `newSettle()`: `pjtIds`, `mandayBreakdown`, `mandayOverride` 필드 초기화
- `mandayColForPjt(pid)`, `rosterColForPjt(pid)`: 기존 `getLinkMandayCol()`은 `settleDraft.pjtId` 전역 기준이라, 임의의 프로젝트 id를 받는 버전을 신설(다중 합산 시 각 프로젝트마다 다른 컬렉션 조회 필요)
- `mdForPjt(pid)`: 해당 프로젝트의 공수값(수동수정 우선, 없으면 자동집계값)
- `setMandayCard()`: 프로젝트 다중 체크박스 UI 추가, 선택 프로젝트 수에 따라 단일/다중 행 렌더링 분기
- `mandayRowsHtml()`/`refreshMandayRows()`: 표 본문만 갱신(전체 재렌더 없이 입력 반응)
- `toggleMandayPjt(pid)`: 체크박스 토글, 최소 1개는 유지되도록 방어
- `fetchManday()`: 선택된 모든 프로젝트를 순회하며 각자 컬렉션에서 근로자 명부 필터링 후 합산 → `d.mandayBreakdown`에 프로젝트별 저장
- `setSupply()`, `settleLines()`: `method==='manday'`이고 `pjtIds.length>1`이면 프로젝트별로 합산/항목 분리, 아니면 기존 로직 그대로(하위호환)
- `publishSettle()`: 저장 payload에 `pjtIds` 배열 추가
- `renderSettle()` 목록: PJT 필터가 `pjtId` 또는 `pjtIds` 배열 매치 시 노출되도록 확장, 배지도 다중이면 "P4 Ph2 (FAB) + P4 Ph4 (SUP)"처럼 표시
- `openSettle()` 상세, `settleDocHTML()` 인쇄 템플릿의 프로젝트 라벨도 동일하게 다중 대응

## 적용 범위

"공수 연동"(manday) 방식에만 적용. "공정 자동"(progress)·"수량 정산"(qty) 방식은 견적서 자체가 프로젝트별로 종속되어 있어(`estimates.filter(e=>e.pjtId===d.pjtId)`) 이번 범위에서 제외. 필요 시 별도 확장 요청.

## 검증

- Node.js로 다중 프로젝트 합산 계산 로직 시뮬레이션: FAB 120.0공수 + SUP 62.6공수 × 190,000원 = 34,694,000원 정확히 산출 확인. 프로젝트별 수동수정(override) 반영도 확인
- `node --check`로 `gihoek/index.html` 유일한 `<script type="module">` 블록 문법 검증 통과
- 함수 중복 선언 여부 grep으로 확인 (중복 없음)

## 배포

- `gihoek/index.html` (5.3.12 → 5.3.15)
- 루트 `index.html` 버전배너 갱신 (build 20260818e)
- 백업: `backup/v5.3.15/gihoek/index.html`
- 문서: `docs/1_4_gihoek_settle.md` r8 갱신
- 프로덕션 직접 배포
