# 4.1. PJT 관리 — P4 Ph2 FAB (홈 · 오늘 · 주간 · 캘린더)

> 앱: `portal/pjt/index.html` · 워커 컬렉션: `pjt_workers_fab`
> Firestore: `user_schedules`, `daily_reports_{날짜}`, `daily_report_docs`, `pjt_workers_fab`, `edoc_leave`
> 최초 작성: 2026-07-01 · 최종 개정: 2026-07-27 (접근검증 게이트 추가) · 작성: 춘식이(Claude)

---

## 접근 검증 (2026-07-27)

- 기존엔 Firebase Auth 자체가 없어 URL(`.../pjt/`)로 직접 열면 로그인 여부와 무관하게 전체 화면·데이터가 노출됐음
- 모듈 스크립트 상단에 로그인+`portal_users` 검증(`status==='approved' && (admin || perms.pjt)`) 게이트 추가. 검증 통과 전엔 전체 화면을 오버레이로 가리고, `window._accessGranted`가 `true`가 되기 전엔 아래 항목이 실행되지 않음:
  - `waitForFirebaseAndInit()` 폴링 조건에 `window._accessGranted` 추가 — 이 함수가 트리거하는 전체 UI 초기화 캐스케이드가 검증 통과 전엔 시작되지 않음
  - 공수 preload, 공정 데이터 preload (모듈 최상단 즉시실행 IIFE 2곳)
  - `subscribeUserSchedules()`, `subscribeEdocLeave()` 실시간 구독 2곳
  - `applyOnLoad()`(설정 자동 반영), `renderProgress()` 최초 호출
- ⚠️ 파일이 4천 줄 이상으로 크고 데이터 로딩 지점이 여러 곳에 흩어져 있어, 위 목록이 발견된 최상위 자동실행 지점의 전부이지만 100% 전수 검증은 아님. 최종 방어선은 Firestore 보안 규칙임을 유의.


## 탭 구성

상단 탭바(`switchTabPC` / `switchTab`)로 전환: 홈 · 오늘 · 주간 · 캘린더 · 근태 · 공정 · 설정. (근태·공정은 별도 문서)

---

## 4.1.0 홈 / 4.1.1 오늘

- **홈**: 프로젝트 대시보드, 진입 메뉴 카드
- **오늘**: 업무보고(`daily_reports_{날짜}`, 날짜별 컬렉션 분리) + 일일 보고서 문서(`daily_report_docs/{dateKey}`)

### 공사일보 조회 수정/삭제 (4.5.0 신규)

- 공사일보 조회 상세 모달(`openDRDetail` → `renderDRView`) 하단에 **✏️ 수정 / 🗑 삭제** 버튼 추가 (기존 조회·PDF 유지)
- **수정**(`editDRDetail`): 편집 폼 전환 → `saveDRDetail`이 `_fbUpdateReportDoc`(= `setDoc merge` + `updatedAt`) 호출 → 즉시 상세 반영. `cancelDREdit`로 원본 복귀
- **삭제**(`deleteDRDetail`): confirm 후 `_fbDeleteReportDoc`(= `deleteDoc`) → 목록 자동 복귀
- 수정 가능 필드: 작성자·금일작업·명일예정·투입인원·사용장비·특이사항. **현장명·작성일자는 문서 키(날짜) 근거라 고정**
- 뷰/편집 버튼 그룹 토글(`toggleDRBtns`), XSS 방지 이스케이프(`_drEsc`) 적용
- 컬렉션: `daily_report_docs` (문서 ID = 날짜키)

### 작성자 드롭다운 버그 수정 (4.5.1)

- **증상**: `daily-report/index.html`(공사일보 작성, standalone 창)에서 작성자 선택이 비어있고 로그인 계정 자동 선택도 안 됨
- **원인**: standalone 창은 메인 포털의 Firebase Auth 컨텍스트가 없어 `portal_users` 컬렉션 `getDocs` 조회가 실패 → 기존 코드는 `catch(e){}`로 조용히 무시해 드롭다운이 완전히 빈 채로 남음
- **수정**: Firestore 조회는 try/catch로 감싸 실패 시 `console.warn` 로그만 남기고, 조회 성공/실패와 무관하게 `localStorage`(`jh_login_full`/`jh_login_name`)의 로그인 계정은 항상 옵션에 추가 + 자동 선택
- 대상 파일: `daily-report/index.html`(FAB) · `daily-report/ph4.html`(SUP) 동일 수정

---

## 4.1.2 주간 (twoweek) — 4.4.0 갱신

- 2주치 일정을 7열 grid로 표시 (`renderTwoWeek`)
- **좌우 이동 추가**: 상단 네비게이터 `‹ 날짜범위 ›` + `오늘` 버튼. 2주 블록 단위로 앞뒤 이동
  - 상태 `window._twBlock`(2주 블록 오프셋), `changeTwoWeek(dir)` / `goTwoWeekToday()`
  - 오프셋 0일 때만 "이번 주 / 다음 주" 라벨 표시
- `user_schedules` 기반 + `edoc_leave`(연차) 연동

---

## 4.1.3 캘린더 (calendar) — 4.4.0 갱신

- 월 단위 캘린더, 좌(달력) 우(선택일 상세) 분할
- **월간 일정 CRUD 추가**: 우측 패널에 `＋ 이 날 일정 등록` 버튼(선택 날짜 자동 입력) + 사용자 등록 일정 탭 시 수정·삭제(`openUsDetail`). 고정 일정은 읽기 전용 유지
- **년월 점프 추가**: 좌측 상단 `yyyy년 mm월` 클릭 시 월 선택기(`openCalMonthPicker`/`pickCalMonth`)로 원하는 시점 이동
- **일정 등록자 자동 반영 (격리/로그인 연동)**: 등록창(`openUsForm`) 등록자 칸을 로그인 계정으로 자동 채움 — `localStorage.jh_login_full || jh_login_name` 우선, 없으면 기존 방식 폴백. 포털 로그인 시 계정명을 같은 origin localStorage에 저장

### 자정 넘기는 일정 시작일에만 표시 (4.5.2)

- **배경**: 다중일 일정(`sdate`≠`edate`)은 기존에 start/mid/end로 매일 렌더됨. 하지만 "19:00~다음날 05:00"처럼 저녁에 시작해 자정을 넘겨 새벽에 끝나는 일정도 동일하게 처리되어 다음날에도 중복 표시되는 문제가 있었음
- **판별 로직**(`_usItemsForKey`): 종료일이 시작일의 정확히 다음날이고, 종료시각(`etime`)이 시작시각(`stime`)보다 빠르거나 같으면 "자정 넘김"으로 판단 → 표시상으로만 종료일을 시작일과 동일하게 압축해 시작일에만 노출
- 3박4일 출장처럼 진짜 여러 날짜에 걸친 일정(종료시각이 시작시각보다 늦은 경우)은 이 조건에 해당하지 않아 기존처럼 각 날짜에 계속 표시됨
- 상세보기/수정(`openUsDetail`/`_detailEdit`)에는 원본 종료일·시간이 그대로 보존되어 정확한 일시 정보 확인·수정 가능
- 대상 파일: `pjt/index.html`(FAB) · `pjt_ph4/index.html`(SUP) 동일 수정, 모바일(`m/pjt.html`)은 애초에 다중일 렌더링을 하지 않아 해당 없음

### user_schedules 컬렉션
```js
user_schedules/{auto-id}: { sdate, edate?, stime?, tag, text, reg, ..., savedAt }
```
- 구독 `onSnapshot`, 추가 `addSchedule` / 삭제 / 수정. 갱신 시 현재 탭 자동 리렌더

---

## 워커 (pjt_workers_fab)

`{ name, order, ... }` — `order`로 정렬. 추가·삭제 가능.

