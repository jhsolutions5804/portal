# 4.0. PJT 관리 — 홈

> 포털 메뉴: `pjt`(P4 Ph2 FAB), `p4ph4`(P4 Ph4 SUP), `reg_*`(경량 PJT, 동적), `pjt_manday`(월간 공수)
> 최초 작성: 2026-07-01 · 최종 개정: 2026-07-24 (5.0.0) · 작성: 춘식이(Claude)

---

## 개요

PJT 관리는 진행 중인 현장 프로젝트별 워크스페이스를 제공한다. 포털 홈에서 "PJT 관리" 메뉴 진입 시, 현재 운영 중인 프로젝트 목록(`showPjtHome`)에서 선택한다.

---

## 프로젝트 목록 (PJT_SUBTABS)

| key | 명칭 | 종류 | 앱 경로 | 워커 컬렉션 |
|-----|------|------|---------|-------------|
| `pjt_home` | PJT 홈 | 고정 | (포털 내장) | - |
| `p4ph2` | P4 Ph2 (FAB) | 고정 | `portal/pjt/` | `pjt_workers_fab` |
| `p4ph4` | P4 Ph4 (SUP) | 고정 | `portal/pjt_ph4/` | `pjt_workers_ph4` |
| `reg_{id}` | 신규 등록 PJT (경량) | 동적 | `portal/pjt_light/?pjtId={id}` | `pjt_registry/{id}/workers` |
| `pjt_manday` | 월간 공수 | 고정(항상 최하단) | `portal/pjt_manday/` | (마스터 명부 참조) |

> 상세는 4.1(FAB), 4.2(SUP), 4.3(경량 PJT), 4.4(월간 공수·마스터 명부) 문서 참조.

---

## 신규 PJT 자동 편입 (5.0.0 신규)

- **등록**: PJT 홈 우측 상단 `＋ 신규 PJT` → `pjt_registry` 컬렉션에 문서 생성(`saveNewPjt`). 워크스페이스 URL을 비워두면 자동으로 경량 PJT 워크스페이스(`pjt_light/`) 연결
- **자동 편입**: `syncPjtRegistrySubtabs()`가 로그인 시·PJT홈 진입 시·등록/종료/재개 시 `pjt_registry`의 `active` 문서를 `PJT_SUBTABS` 배열에 자동 추가 → 사이드바 메뉴 + 상단 카드(KPI: 공정율·D+·누적공수)에 P4 Ph2/Ph4와 동일하게 표시
- **삽입 위치**: 신규 항목은 항상 `pjt_manday`(월간 공수) **바로 앞**에 삽입 — 월간 공수는 항상 최하단 고정
- **KPI 소스**: 경량 PJT(`reg_*`)는 `pjt_registry/{id}` 문서의 `progress`/`manday`/`startDate` 필드를 직접 읽음 (FAB/SUP처럼 zone 기반 계산 없음). `progress`/`manday`는 경량 워크스페이스의 품목 체크·근태공수 저장 시 자동 갱신(`recalcProgress`/`recalcTotalManday`)
- **관리자 설정**: 카드 ⚙️ 버튼 → `openPjtSettings('reg_{id}', name)` — 기본정보 수정 + 종료 처리(`endPjtFromSettings`). 진행률/누적공수는 워크스페이스에서 자동계산되므로 읽기 전용
- **종료 시**: `pjt_registry` 문서 `status:'ended'` → 카드·사이드바에서 자동 제거, PJT 홈 하단 "종료된 프로젝트" 목록으로 이동(재개 가능)

---

## 공통 구조 (FAB/SUP)

두 프로젝트 앱(FAB/SUP)은 **동일한 코드 베이스**이며, 차이는 워커 컬렉션명과 localStorage 키(`fabls_`/`ph4ls_`)뿐이다. 각 앱은 6개 탭으로 구성된다: 홈 · 오늘 · 주간 · 캘린더 · 근태 · 공정 · 설정.

> ⚠️ **공수/출역 컬렉션은 FAB·SUP가 서로 다름 (공유 아님)**: FAB는 `worker_manday`/`worker_attendance`, SUP는 `ph4_manday`/`ph4_attendance`. 과거 "공유 컬렉션"으로 잘못 가정했던 이력 있음 — 월간 공수 집계 시 반드시 각 컬렉션을 별도로 읽어야 함(4.4 참조).

---

## 설정 탭 (settings) — 4.3.0

각 PJT 앱 상단 탭바에 `⚙️ 설정` 탭. 신규 PJT 등록 정보(명칭/현장/거래처/내용/품목/물량/공사 시작일)를 수정하며 `pjt_settings/{key}`에 저장. 저장 시 헤더 실시간 반영, 공사 시작일 저장 시 D+ 자동 계산.

---

## 포털 PJT 홈 레이아웃 — 통합 캘린더 (4.4.0, 개편)

> 기존 하이브리드(축소카드 + 타임라인 2단, 4.3.0)에서 **통합 월간 캘린더**로 전면 개편.

포털 "PJT 관리" 진입 시 홈(`showPjtHome` → `renderPjtHomeCards` + `renderPjtRegistry` + `loadPjtCalendar`) 구성:

- **상단**: PJT별 요약 카드 (`pjt-cards-row`) — 명칭·바로가기 + 공정율·D+·누적공수
  - 배치: **가로 스크롤**(카드 고정폭 460px, `flex-wrap:nowrap; overflow-x:auto`). 화면이 좁아져도 세로로 접히지 않고 옆으로 스크롤. 신규 PJT 증가 시 계속 가로로 나열
- **하단**: 통합 월간 캘린더 2단 (`pjt-cal-grid`, 좌 1.4 : 우 1)
  - **좌(캘린더)**: 전체 PJT 일정을 월 단위로 표시. 년월 이동(`pjtCalShift`), 날짜별 태그 색점, 오늘/선택일 강조. 태그 색상 — 반입 `#1D5BA6` · 검수 `#2e7d32` · 교육 `#5e35b1` · 휴무 `#c0392b` · 연차 `#e67e22`
  - **우(상세)**: 날짜 클릭(`pjtCalSelectDay`) 시 그 날 전체 PJT 일정 + 그 날짜 업무지시·보고 함께 표시
  - 데이터: 일정 `user_schedules`(p4ph2) + `ph4_schedules`(p4ph4), 업무지시 `daily_report_docs` + `ph4_reports`(문서 ID = 날짜)
- **컨테이너**: 전체 폭 사용(`width:100%`), 좌측 사이드바 옆부터 화면 우측까지 (여백 축소)
- **레이아웃 구현 주의**: 캘린더 격자(요일·날짜 7열)는 미디어쿼리 클래스 대신 **요소 인라인 스타일**로 `display:grid; grid-template-columns:repeat(7,1fr)` 고정 → 화면 폭·미디어쿼리 무관하게 항상 정상 표시 (이력: 클래스가 특정 조건에서 미적용되던 문제 회피)

---

## 홈 일정 상세/등록/수정/삭제 (4.5.0 신규)

> 포털 홈 우측 상세 패널(`pjt-cal-detail`)에서 일정을 직접 조회·관리. 별도 PJT 앱 진입 없이 홈에서 완결.

- **상세 조회**: 우측 패널의 각 일정 클릭(`openHomeSchedDetail`) → 상세 모달(`home-sched-detail-modal`). 카테고리·일정·기간·장소·참석자·등록자·프로젝트 표시
- **등록**: 우측 패널 상단 `＋ 일정 등록`(`openHomeSchedForm('new', dk)`) → 폼 모달(`home-sched-form-modal`). 프로젝트 선택·내용·카테고리(칩)·시작/종료 일시(date+time)·장소·참석자·등록자
- **수정**: 상세 모달 `✏️ 수정`(`editHomeSchedFromDetail` → `openHomeSchedForm('edit')`). 값 채워 열림, 저장 시 원본 갱신. **프로젝트(컬렉션)는 안전상 고정**
- **삭제**: 상세 모달 `🗑 삭제`(`deleteHomeSched`). 확인창 후 삭제
- **저장 로직**: 신규 `addDoc` / 수정 `setDoc(merge)` / 삭제 `deleteDoc`. 저장/삭제 후 `loadPjtCalendar()` + `pjtCalSelectDay()` 자동 새로고침
- **컬렉션**: 선택 PJT에 따라 `user_schedules`(p4ph2) / `ph4_schedules`(p4ph4)
- **필드**: `reg`·`text`·`place`·`att`·`tag`·`tagLabel`·`sdate`·`edate`·`stime`·`etime`·`isTodo`·`savedAt` — **PJT 앱 일정과 완전 동일** → 홈·PJT 앱 양방향 호환
- **캐시**: `_pjtCalCache`에 문서 `id`·`col` 저장(수정/삭제 대상 식별용). 기존 소비처는 `tag`·`stime`만 읽어 영향 없음
- **카테고리**: 반입·검수·교육·회의·설치·안전·휴무·연차·행정 (`HOME_SCHED_CATS`, 홈 캘린더 태그색과 동일)
- **적용 범위**: PC 전용(모바일은 `m/home.html` 리다이렉트). 모달 z-index 40(기존 프로필 모달과 동일)

---

## Firebase / 인프라

- **운영(portal)**: 프로젝트 `p4ph2-fab-506a7` (전체 공용)
- **테섭(portal-test)**: 프로젝트 `portal-test-6e0ff`로 **완전 격리** (2026-07-02 완료). 전 모듈이 테스트 프로젝트 사용 → 테섭 입력이 운영 데이터에 영향 없음
- **`.nojekyll`**: 운영·테섭 양쪽 루트에 추가. GitHub Pages의 Jekyll 빌드를 건너뛰어 빌드 실패·지연 방지 (미추가 시 Page build failed 반복)
- 포털 임베드 시 기존 사이드바·탭바 숨김, 자체 상단 탭바 사용
