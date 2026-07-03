# 4.1. PJT 관리 — P4 Ph2 FAB (홈 · 오늘 · 주간 · 캘린더)

> 앱: `portal/pjt/index.html` · 워커 컬렉션: `pjt_workers_fab`
> Firestore: `user_schedules`, `daily_reports_{날짜}`, `daily_report_docs`, `pjt_workers_fab`, `edoc_leave`
> 최초 작성: 2026-07-01 · 최종 개정: 2026-07-02 (4.4.0) · 작성: 춘식이(Claude)

---

## 탭 구성

상단 탭바(`switchTabPC` / `switchTab`)로 전환: 홈 · 오늘 · 주간 · 캘린더 · 근태 · 공정 · 설정. (근태·공정은 별도 문서)

---

## 4.1.0 홈 / 4.1.1 오늘

- **홈**: 프로젝트 대시보드, 진입 메뉴 카드
- **오늘**: 업무보고(`daily_reports_{날짜}`, 날짜별 컬렉션 분리) + 일일 보고서 문서(`daily_report_docs/{dateKey}`)

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

### user_schedules 컬렉션
```js
user_schedules/{auto-id}: { sdate, edate?, stime?, tag, text, reg, ..., savedAt }
```
- 구독 `onSnapshot`, 추가 `addSchedule` / 삭제 / 수정. 갱신 시 현재 탭 자동 리렌더

---

## 워커 (pjt_workers_fab)

`{ name, order, ... }` — `order`로 정렬. 추가·삭제 가능.
