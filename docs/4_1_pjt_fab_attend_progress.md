# 4.1. PJT 관리 — P4 Ph2 FAB (근태 · 공정)

> 앱: `portal/pjt/index.html`
> Firestore: `worker_attendance`, `worker_manday`, `progress_checks_{날짜}`, `pjt_workers_fab`
> 최초 작성: 2026-07-01 · 최종 개정: 2026-07-02 (4.4.0) · 작성: 춘식이(Claude)

---

## 4.1.4 근태 (attend) — 4.4.0 갱신

기술인(현장 작업자)의 출역·공수를 관리한다.

### 화면 구성
- 좌측: 기술인 출역 현황(체크) + 공수 입력(`+`/`-` 또는 직접 입력)
- 출역 인원 카운트 배지(`att-worker-count`)
- 출역현황 목록 상단 **일괄 조작 바** (4.4.0 신규):
  - **왼쪽 `전체 출역 체크/해제`** (`toggleAllWorkers`) — 전원 미체크/일부 체크면 전체 체크, 전원 체크 상태면 전체 해제. 버튼 라벨·색상 토글
  - **오른쪽 `전체 공수` 입력 + `일괄 적용`** (`applyAllManday`→`setAllManday`) — 입력값(0~3, 소수 1자리)으로 전원 공수 일괄 설정, `0` 입력 시 전원 초기화
- "📋 이달 공수 집계표 보기" 모달(`openKongsuModal`)

### 데이터
```js
worker_attendance/{dateKey}: { checks:[workerId,...], updatedAt }   // 출역 체크
worker_manday/{dateKey}:     { md:{ workerId: 공수값, ... }, updatedAt }   // 공수
```
- 출역: `_fbGetWorkerChecks` / `_fbToggleWorker`(개별) / **`_fbSetAllWorkers`(일괄, 1회 쓰기)**
- 공수: `_fbGetManday` / `setMandayInput`(개별) / **`_fbSetManday`(맵 일괄 저장)** — 일괄 조정은 이 함수 재사용
- 낙관적 UI 즉시 반영 후 Firestore 저장. 일괄은 개별 반복 호출 대신 **1회 쓰기**로 처리(경합·낭비 방지)

### 홈 KPI 연동
- 이달 누적 공수(`home-manday`), 오늘 출역(`home-att`), PC 상단 누적공수(`pc-manday-total`). `_mandayCache` 백그라운드 preload

---

## 4.1.5 공정 (progress)

작업 구역(zone)별 공정 진행 체크. `progress_checks_{날짜}/{zoneId}` (날짜별 컬렉션 분리, zone 단위 문서). 2분할 레이아웃, `_renderProgressUI()`로 구독 갱신.

### 공정표 PPT 내보내기 (`generateProgressPPT`) — 4.5.0 (2026-07-03)

상단 `📊 공정표 PPT` 버튼 → 기준일 선택(`openPptDateModal`) 후 PptxGenJS로 `.pptx` 생성·다운로드. 파일명 `{YYYYMMDD}_귀뚜라미범양냉방_공정진행율.pptx`.

- **1P 갑지 · 2P 공정 현황(6섹터 카드) · 3~8P 섹터별 상세**(2026-07-03 추가, 섹터당 1P)
- 상세페이지 = 섹터별 4단계(반입/입고검사/설치/시공검측) 표. 컬럼: 전일·금일·누계·증감·공정율·진행바
  - **전일** = `prevStats`(전일 누계) · **누계** = `todayStats`(당일 누계) · **금일** = 누계−전일 · **증감** = +금일 · **공정율** = 누계/total
  - 기존 `calcZone`/`getCksProg` 재사용 → **추가 Firestore 쿼리 없음**
  - 활동 없는 섹터: 값 `0` + 진행바 `-`
- 삽입 위치: `generateProgressPPT` 내 `// 다운로드` 직전 (`todayStats.forEach`)

