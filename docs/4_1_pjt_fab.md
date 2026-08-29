# 4.1. PJT 관리 — P4 Ph2 FAB (홈 · 오늘 · 주간 · 캘린더)

> 앱: `portal/pjt/index.html` · 워커 컬렉션: `pjt_workers_fab`
> Firestore: `user_schedules`, `daily_reports_{날짜}`, `daily_report_docs`, `pjt_workers_fab`, `edoc_leave`
> 최초 작성: 2026-07-01 · 최종 개정: 2026-08-29 (업무일지 출퇴근시간 입력 추가) -22 (근태 출역 인원수 카운트 버그 수정, v5.3.5 / daily-report 2.4.2) · 작성: 춘식이(Claude)

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

### 저장 실패(Missing or insufficient permissions) 근본 원인 수정 + 접근 게이트 신설 (v2.4.1)

- **증상**: `daily-report/index.html`에서 항목 작성 후 저장 시 항상 "저장 실패: Missing or insufficient permissions." 알림 발생 (근태 인원수 자동 로드 등 일부 조회도 동일 오류)
- **원인**: `daily-report/index.html`은 `firebase-app.js` · `firebase-firestore.js`만 import하고 **`firebase-auth.js`를 import하거나 `getAuth(app)`을 호출하는 코드가 아예 없었음**. 다른 모든 모듈(`pjt`, `pjt_ph4`, `edoc`, `hr`, `gihoek`)은 각자 독립적으로 `getAuth(app)`을 호출해 Firestore 요청에 로그인 토큰을 실어 보내는데, `daily-report`만 이 초기화가 빠져 있어 항상 미인증 상태로 Firestore에 요청 → 로그인을 요구하는 보안 규칙에 의해 거부됨. (4.5.1의 "작성자 드롭다운 버그"도 동일 원인의 다른 증상이었으나 당시엔 try/catch로 조용히 무시되어 저장 실패만큼 눈에 띄지 않았음)
- **수정**: `pjt/index.html`과 동일한 패턴으로 `firebase-auth.js` import + `getAuth(app)` 추가. 아울러 접근 게이트(`_accessGatePromise`)를 신설해 로그인 여부와 `portal_users` 권한(`status==='approved' && (admin===true || perms.pjt===true)`)을 확인 후에만 화면 사용을 허용하도록 함 — 공사일보 작성 권한 기준은 PJT 권한(`perms.pjt`)과 동일하게 통일(대표 확인 완료)
- 대상 파일: `daily-report/index.html`(FAB). `ph4.html`(SUP)은 별도 확인 필요 — 미반영 상태
- 검증: `node --check` 문법 검증 → portal-test(`jhsolutions5804.github.io/portal-test/daily-report/`) 실 저장 테스트 통과 확인 후 프로덕션 배포

---

### 근태 출역 인원수 카운트 버그 수정 (v5.3.5 / daily-report 2.4.2)

- **배경**: 근태 탭 "기술인 출역 현황"에 "출역 9명 / 전체 5명"처럼 출역 인원이 전체 인원보다 많게 표시되는 걸 대표가 발견. 공사일보 "기술인 투입 현황"도 마찬가지로 실제 현재 인원(5명)보다 많은 숫자(9명)로 표시됨
- **원인 (2가지가 섞여 있었음)**:
  1. `worker_attendance/{날짜}` 문서의 `checks` 배열은 그 날짜 당시 실제로 체크된 인원 ID를 그대로 보존 — 이후 명단(`pjt_workers_fab`)에서 인원이 삭제돼도 과거 체크 기록 자체는 지워지지 않음(의도된 동작, 삭제 확인창에도 "기존 공수·출역 데이터는 유지됩니다"라고 안내). 그런데 "출역 N명" 배지와 공사일보 "투입 현황"은 이 `checks.length`를 **필터링 없이 그대로** 표시하고 있어서, 명단에서 삭제된 인원의 과거 체크까지 숫자에 포함되어 실제 화면에 보이는 인원 수보다 많게 나옴
  2. 공사일보(`daily-report/index.html`)의 "전체 N명"은 `data.js`에 **하드코딩된 정적 `WORKERS` 배열**(w1~w9, 9명 고정)을 그대로 썼음 — 근태 탭에서 실제 명단을 추가/삭제해도 이 하드코딩 목록은 전혀 갱신되지 않아 현재 인원(5명)과 무관하게 항상 옛 숫자가 표시됨
- **수정**:
  - `pjt/index.html` — "출역 N명" 배지, 홈 화면 "오늘 출역" KPI 모두 `checks`를 현재 명단(`_ws`/`getWorkers()`)에 실제로 존재하는 ID로 필터링한 뒤 카운트하도록 수정 (명단에서 삭제된 인원의 과거 체크는 카운트에서 제외)
  - `daily-report/index.html` — 하드코딩 `WORKERS` 배열 참조 제거, `pjt_workers_fab` + `master_workers`(퇴사일)를 실시간 조회해서 "전체 인원"을 계산하도록 변경. "출역 인원"도 동일하게 현재 유효 명단 기준으로 필터링
  - **검토했으나 보류한 대안**: 삭제된 인원을 "◯◯◯ (삭제됨)" 형태로 화면에 같이 표시하는 방안도 시도했으나, 마스터 명부에 연결 안 된 채 추가됐던 인원은 삭제 후 이름을 복구할 방법이 없어 "알 수 없음"으로만 표시되는 문제가 있어 대표 확인 하에 **화면에 안 보이게 하고, 카운트에서도 제외**하는 방식으로 확정
- 검증: `node --check` → portal-test 실사용 테스트(8/21 날짜 기준 "출역 5명 / 전체 5명" 확인) → 프로덕션 배포

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

---

## 주간공정회의 자료 자동생성 + 도면 좌표 매핑 (v5.3.0, 2026-07-30)

홈 화면 바로가기 카드 2개 추가: **🗓️ 주간공정회의 자료**, **🗺️ 도면 매핑**

### 주간공정회의 자료 (`generateWeeklyReportPPT`)

- **주차 계산**: 앵커 30주차 = 2026-07-15(수)~07-21(화). `wrSnapToTuesday()`로 선택일을 그 주기의 화요일(마감일)로 스냅 → `wrCalcWeekNo()`로 앵커 대비 ±7일 단위 주차 산출
- **데이터**: 기존 공정 탭의 `_fbGetProgChecks(dateKey, zoneId)`를 전주/금주 화요일 날짜로 각각 호출해 전주 누계·금주 누계·금주(증분)·공정률 계산 (별도 히스토리 저장 없이 기존 일별 체크 스냅샷 메커니즘 재사용)
- **슬라이드**: 구역(3F FIZ·X-OB·복합3동·복합4동·W-OB·2F 제조부속실) 당 1장, 총 6장. 상단 도면(구역별 원본 비율 유지, `wrFitContain()`으로 박스 안에 중앙정렬) + 우측 화살표 flow형 범례(항상 원색 고정, 최전선 진행단계만 bold) + 하단 비교표(Step·공정률도 원색 고정)
- **도면 위 박스 마커**: `zone_layouts`에 좌표가 있는 장비만, 해당 주차 체크 상태의 최종 단계 색상으로 투명도 33% 박스 표시
- **파일명**: `{WW}주차_귀뚜라미범양냉방_P4_PH2(FAB)_주간공정회의자료.pptx`
- 도면 이미지는 `assets/floorplans/{zoneId}.png` (브라우저 `Image` 프리로드로 존재여부·원본크기 사전 확인 후 배치 — `addImage()`가 브라우저에서 비동기 실패를 즉시 못 잡는 특성 때문에 반드시 사전 체크 필요)

### 도면 좌표 매핑 툴 (`openLayoutMapModal`)

- Firestore `zone_layouts/{zoneId}`: `{ points: { [eqId]: {x,y,w,h} }, updatedAt }` — 도면 원본 크기 대비 0~1 정규화 비율로 저장 (해상도 무관 재사용 가능)
- **배치 방식**: 장비 1개는 드래그로 정확히 크기를 잡고, 이후부터는 클릭 한 번으로 그 평균 크기(`lmGetRefSize`)가 자동 적용 (8px 미만 이동은 클릭으로 판정)
- **자동정렬 스냅** (`lmSnapToAlignment`): 직전 배치한 박스 최대 4개의 중심점 분산을 비교해 가로/세로 일렬 여부 판정, 클릭 좌표 중 정렬축과 수직인 성분만 그 줄의 평균값으로 스냅 (다른 줄로 이동 시 자동 감지해 스냅 안 함)
- **크기 일괄 보정** (`lmNormalizeSizes`): 이미 찍힌 박스들의 중심점은 유지한 채 크기만 중앙값으로 통일
- **구역 전체 삭제** (`lmDeleteAll`): 2단계 확인 후 해당 구역 좌표 전체 초기화
- **확대/축소**: 50~400%, `lm-scrollbox`(overflow:auto)로 스크롤 팬. 구역 전환 시 100%로 초기화
- 마커 색상(반입=진한파랑 1D5BA6·입고검사=연한파랑 5BA4CF·설치=초록 16A34A·시공검측=보라 7C3AED)은 범례·표와 동일 팔레트

### 장비 ID 목록 (`ZONES`)

| 구역 id | 명칭 | 총수량 | 장비ID 규칙 |
|---|---|---|---|
| fiz | 3F FIZ | 39 | 801~839 |
| xob | X-OB | 19 | 861~879 |
| c3 | 복합3동 | 14 | 351~364 |
| c4 | 복합4동 | 14 | 302A~302N |
| wob | W-OB | 81 | 801~881 |
| mfr | 2F 제조부속실 | 16 | 801,802,811~824 |

⚠️ fiz/wob/mfr 구역 간 장비ID 문자열이 중복되나(예: `801`), `zone_layouts`·체크 데이터 모두 구역별로 컬렉션/문서가 분리돼 있어 실사용상 충돌 없음.

### 데이터 이관

좌표 매핑은 portal-test Firebase(`portal-test-6e0ff`)에서 먼저 진행 후, `scripts/migrate_zone_layouts.py`(firebase-admin, 로컬 실행)로 프로덕션(`p4ph2-fab-506a7`)에 복사하는 방식 사용. 2026-07-30 최초 이관 완료.




---

## 업무일지(daily-report) 출퇴근시간 입력 추가 (2026-08-29)

`daily-report/index.html` 작성 폼에 "④ 근무시간" 카드 신규 — 출근/퇴근시간(10분 단위 스냅, `step="600"` 무시하는 브라우저 대응해 change 이벤트로 재보정) + 휴게시간(기본 2h) 입력, 근무시간 자동표시. Firestore 저장 시 `checkIn`/`checkOut` 필드로 함께 저장. 카드 번호 4~9로 재정렬(금일작업→5, 명일예정→6, 기술인투입→7, 사용장비→8, 특이사항→9).

이 출퇴근시간은 **업무일지 자체의 참고 정보**이며, 인사 근로시간 자동계산에 쓰이는 `worker_attendance_log`(edoc 출퇴근 기록 탭에서 별도 기록)와는 무관한 별개 데이터임 — 혼동 주의. 상세: `2_8_hr_worktime.md`.
