# 4.1. PJT 관리 — P4 Ph2 FAB (근태 · 공정)

> 앱: `portal/pjt/index.html`
> Firestore: `worker_attendance`, `worker_manday`, `progress_checks_{날짜}`, `pjt_workers_fab`
> 최초 작성: 2026-07-01 · 최종 개정: 2026-08-18 (4.10.6) · 작성: 춘식이(Claude)

---

## 4.1.4 근태 (attend) — 4.4.0 갱신

### 기술인 명단 관리 (`toggleWorkerMgmt` → 명단 관리 패널) — 4.10.4 갱신

출역 현황 상단 "⚙️ 명단 관리" 버튼으로 여닫는 패널. 현재 PJT에 투입된 기술인 목록(`pjt_workers_fab`)을 관리한다.

- **추가**: 마스터 명부(`master_workers`)에서 선택 → `_fbAddWorkerFromMaster`
- **수정** (4.10.4 신규): 각 인원 옆 "수정" 버튼 → 이름 · 생년월일 인라인 편집 모드 전환 → "저장"/"취소". `_fbUpdateWorker(workerId, {name, birth})`로 일괄 저장
  - 이전에는 생년월일이 비어있는 인원만 최초 1회 입력 가능했고, 이미 값이 있는 인원의 이름·생년월일은 전혀 수정할 방법이 없었음(버그)
  - 생년월일 입력은 네이티브 `<input type="date">` 대신 텍스트 입력 + 자동 하이픈 마스킹(`_maskBirthInput`) 방식으로 전환. 기존 방식은 한 자리 숫자 입력 후 짧게 멈추면 브라우저가 자동으로 값을 확정하고 다음 칸(월)으로 넘어가버려, "10"을 입력하려 해도 "01"만 저장되는 문제가 있었음
  - 형식 검증: `YYYY-MM-DD` (미입력은 허용)
- **삭제**: `_fbDeleteWorker` (기존 공수·출역 데이터는 유지)
- **퇴사처리/재직전환** (4.10.6 신규): 각 인원 옆 퇴사처리 버튼 → 근로자 마스터 명부(`master_workers`)에 `resigned`/`resignedDate` 직접 반영(이 PJT의 `pjt_workers_fab` 문서는 건드리지 않음). 퇴사자는 회색 취소선 + "퇴사 · 날짜" 배지로 표시, "재직 전환" 버튼으로 되돌리기 가능
  - 팀장으로 지정된 인원은 퇴사처리 불가 (마스터 명부 화면과 동일 규칙)
  - 상세 관리(팀 소속 변경, 팀 단가 등)는 `PJT 관리 → 월간 공수 → 근로자 마스터 관리`에서


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
- **설치 진행도(2026-07-03)**: 상세페이지 설치 행의 공정율·진행바는 2페이지와 동일하게 `instBarPct`(설치 5개 항목 부분 진행률) 사용 → 완료 대수 0이어도 진행도 반영. 대수 컬럼(전일/금일/누계/증감)은 완료 대수(`instDone`) 유지
- **섹터 전체 공정율(2026-07-03)**: 상세페이지 헤더 우측에 섹터 전체 공정율(`z.pct`, 8단계 전체 체크 기준) + 전일 대비 증감 표시

