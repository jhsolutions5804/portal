# 4.0. PJT 관리 — 홈

> 포털 메뉴: `pjt`(P4 Ph2 FAB), `p4ph4`(P4 Ph4 SUP)
> 최초 작성: 2026-07-01 · 작성: 춘식이(Claude)

---

## 개요

PJT 관리는 진행 중인 현장 프로젝트별 워크스페이스를 제공한다. 포털 홈에서 "PJT 관리" 메뉴 진입 시, 현재 운영 중인 프로젝트 목록(`showPjtHome`)에서 선택한다.

---

## 프로젝트 목록 (PJT_APPS)

| key | 명칭 | 현장 | 앱 경로 | 워커 컬렉션 |
|-----|------|------|---------|-------------|
| `p4ph2` | P4 Ph2 (FAB) | 귀뚜라미범양냉방 · FCU 설치 | `portal/pjt/` | `pjt_workers_fab` |
| `p4ph4` | P4 Ph4 (SUP) | 귀뚜라미범양냉방 · EHU 설치 | `portal/pjt_ph4/` | `pjt_workers_ph4` |

---

## 공통 구조

두 프로젝트 앱(FAB/SUP)은 **동일한 코드 베이스**이며, 차이는 워커 컬렉션명뿐이다. 각 앱은 6개 탭으로 구성된다:

| 탭 | data-tab | 내용 |
|----|----------|------|
| 홈 | home | 대시보드·진입 메뉴 |
| 오늘 | today | 오늘 업무보고·일정 |
| 주간 | twoweek | 2주 일정 (7열 grid) |
| 캘린더 | calendar | 월 캘린더 |
| 근태 | attend | 출역·공수 입력 |
| 공정 | progress | 공정률 관리 |
| 설정 | settings | 신규 PJT 등록 정보 수정 (4.3.0~) |

> 상세는 4.1(FAB), 4.2(SUP) 문서 참조. 두 앱이 동일 구조이므로 4.1을 기준 문서로 한다.

---

## 설정 탭 (settings) — 4.3.0

각 PJT 앱 상단 탭바(PC/모바일)에 `⚙️ 설정` 탭. 신규 PJT 등록 시 입력한 정보를 수정한다.

| 필드 | 저장 키 |
|------|---------|
| 명칭 / 현장 / 거래처 / 내용 / 품목 / 물량 / 공사 시작일 | `pjt_settings/{key}` (key: `p4ph2`·`p4ph4`) |

- 저장 시 **헤더 실시간 반영** (`applyPjtHeader`): 명칭→헤더 제목, 거래처·내용→부제. 값 없으면 하드코딩 유지
- 공사 시작일 저장 → D+ 자동 계산 + `renderHome()` 즉시 반영, localStorage 동기화
- Firestore 접근은 module 블록 헬퍼(`window._loadPjtSettingsData`/`_savePjtSettingsData`) 경유 (일반 블록에서 `db`·`serverTimestamp` 미접근 회피)

---

## 포털 PJT 홈 레이아웃 (하이브리드) — 4.3.0

포털 "PJT 관리" 진입 시 홈(`showPjtHome`) 구성:

- **상단**: PJT별 축소 요약 카드 2열 (`pjt-cards-row`) — 명칭·바로가기 + 공정율·D+·누적공수 인라인
- **하단**: 타임라인 2단 (`pjt-timeline-grid`)
  - 전체 PJT 주요 일정 — 날짜 시간순, 오늘 노드 강조
  - 업무지시·보고 — 최근순, 각 항목 PJT 태그 (내용 없는 항목 미표시)
- 카드 KPI·일정·보고는 여러 PJT 합산 (`loadPjtStats`, `loadPjtPanels`)
- 메뉴명·설명은 로그인 시 `pjt_settings` 값으로 실시간 갱신 (`syncPjtSubtabsFromSettings`)

---

## Firebase

- 프로젝트 ID: `p4ph2-fab-506a7` (포털 전체 공용)
- 포털 임베드 시 기존 사이드바·탭바 숨김, 자체 상단 탭바(`switchTabPC`) 사용
