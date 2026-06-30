# 4.1. PJT 관리 — P4 Ph2 FAB (홈 · 오늘 · 주간 · 캘린더)

> 앱: `portal/pjt/index.html` · 워커 컬렉션: `pjt_workers_fab`
> Firestore: `user_schedules`, `daily_reports_{날짜}`, `daily_report_docs`, `pjt_workers_fab`, `edoc_leave`
> 최초 작성: 2026-07-01 · 작성: 춘식이(Claude)

---

## 탭 구성

상단 탭바(`switchTabPC` / `switchTab`)로 6개 탭 전환: 홈 · 오늘 · 주간 · 캘린더 · 근태 · 공정. (근태·공정은 4.1 근태·공정 문서 참조)

---

## 4.1.0 홈

- 프로젝트 대시보드. 진입 메뉴(오늘/근태/공정 등 카드)
- 모바일/iframe 포함 기본 CSS 별도 처리

---

## 4.1.1 오늘 (today)

### 업무보고 (daily_reports)
```js
daily_reports_{날짜키}/{auto-id}:   // 예: daily_reports_2026-06-23
{ text, name, time, savedAt }
```
- 날짜별로 컬렉션이 분리됨 (`daily_reports_` + dateKey)
- 작성 시 `addDoc(collection(db, 'daily_reports_'+dateKey), …)`
- 로컬 백업(`fablocal_`) 병행

### 일일 보고서 문서 (daily_report_docs)
```js
daily_report_docs/{dateKey}:
{ dateKey, ... }   // 날짜별 종합 보고 문서
```
- `query(collection(db,'daily_report_docs'), orderBy('dateKey','desc'))`

---

## 4.1.2 주간 (twoweek)

- 2주치 일정을 7열 grid로 표시
- `user_schedules` 기반 일정 + `edoc_leave`(연차) 연동 표시

---

## 4.1.3 캘린더 (calendar)

- 월 단위 캘린더, 좌우 분할 레이아웃
- 일정 표시 소스: `user_schedules`

### user_schedules 컬렉션
```js
user_schedules/{auto-id}:
{
  ...일정 데이터,
  category:  string,    // 자동 추정 + 수동 변경 가능
  savedAt:   serverTimestamp
}
```
- 구독: `query(collection(db,'user_schedules'), orderBy('savedAt','asc'))` → onSnapshot
- 추가 `addSchedule` / 삭제 `delSchedule` / 수정 `updateSchedule`
- 구독 갱신 시 현재 보이는 탭 자동 리렌더

---

## 워커 (pjt_workers_fab)

```js
pjt_workers_fab/{id}:
{ name, order, ... }   // order로 정렬
```
- `query(collection(db, WORKERS_COLLECTION), orderBy('order','asc'))`
