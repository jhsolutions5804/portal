# 7.5. 개발 로그 — PJT 관리

> `portal/pjt/index.html` (FAB) · `portal/pjt_ph4/index.html` (SUP)
> 최초 작성: 2026-06-26 · 작성: 춘식이(Claude)

---

## 커밋 이력 (FAB)

| SHA | 날짜 | 내용 |
|-----|------|------|
| *(초기)* | 2026-06-24 | 5개 탭: 오늘·주간·캘린더·근태·공정 |
| `0649f22a8d` | 2026-06-26 | 과거 실적·공수 preload |
| `05f46a9f50` | 2026-06-26 | B5 날짜 picker (오늘 탭) |
| `014c0d37f4` | 2026-06-26 | C3 6/26 이후 하드코딩 일정 삭제 |
| `a3a0f39470` | 2026-06-26 | B5 fix: today-title/date-picker 구조 분리 |
| `106aab47a8` | 2026-06-26 | B5 최종 fix: `getViewDate()` |
| `253b7125` | 2026-06-26 | fix: via=portal 수신 시 iframe 풀스크린 레이아웃 |
| `7abd5248` | 2026-06-26 | fix(C안): 홈탭 모바일CSS + D+ Firestore 저장/읽기 |
| `46434568` | 2026-06-26 | 완결: 모바일 최종 정리 |

## 커밋 이력 (SUP)

| SHA | 날짜 | 내용 |
|-----|------|------|
| `981da02476` | 2026-06-26 | 과거 실적·공수 preload |
| `c0bc7b179c` | 2026-06-26 | B5 날짜 picker (SUP) |
| `c7a420c1a9` | 2026-06-26 | C3 SUP 확인 |
| `3ddec333cc` | 2026-06-26 | B5 fix SUP |
| `cb037d4a63` | 2026-06-26 | B5 최종 fix SUP |
| `4daed7ef` | 2026-06-26 | fix: via=portal 수신 시 iframe 풀스크린 레이아웃 |
| `2c7efc94` | 2026-06-26 | fix(C안): 홈탭 모바일CSS + D+ Firestore 저장/읽기 |
| `137d7f36` | 2026-06-26 | 완결: 모바일 최종 정리 |

---

## 주요 변경 상세

### PJT-8: 과거 실적·공수 자동 반영

**공정 문제**: `_progCache`가 공정 탭 진입 시에만 채워져 홈/정산에서 공정율 0%

**해결**: 앱 시작 시 시작일~오늘 전체 날짜 × 모든 섹터 공정 자동 preload
- `setTimeout(0)` 지연: ZONES 정의가 IIFE 이후에 위치하는 타이밍 문제 해결

**공수 문제**: preload 범위가 이번 달만 → 과거 달 공수 캐시 누락

**해결**: preload 범위를 시작일~오늘 전체(최대 200일)로 확장

---

### B5: 오늘 탭 날짜 클릭 Picker — 3차례 수정

**1차 문제**: `textContent` 설정 시 자식 노드(date input) 소거
**해결**: today-title div와 date-picker input을 형제 관계로 분리

**2차 문제**: `showPicker()` 미작동
**원인**: `openTodayDatePicker`가 `viewDate`(공정 탭 지역 변수)를 참조
**최종 해결**: `viewDate` 대신 `getViewDate()` 함수 사용

---

### C3: 6/26 이후 하드코딩 일정 삭제

- `ALL_SCHEDULE`에서 2026-06-27 이후 35개 날짜 키 전체 제거
- 잔존: 2026-06-22 ~ 2026-06-26 (5일)

---

### 모바일 대응 (2026-06-26)

#### 문제 1: 포털 iframe 내 그래픽 깨짐

**원인 분석**:
- 홈탭 CSS (`.home-kpi-row`, `.home-kpi-card`, `.home-row2`, `.home-shortcuts`, `.home-sc`) 전체가 `@media(min-width:900px)` 블록 안에만 존재
- 포털 iframe 너비가 모바일 사이즈일 때 CSS가 전혀 적용 안 됨 → div들이 block으로 쌓여 텍스트처럼 표시

**해결**: `</style>` 직전에 모바일 기본값 CSS 추가
```css
/* 모바일 기본 (iframe 포함) */
.home-kpi-row { display:grid; grid-template-columns:1fr 1fr; gap:10px; }
.home-kpi-card { background:#fff; border-radius:12px; padding:14px 16px; }
.home-row2    { display:grid; grid-template-columns:1fr; gap:12px; }
.home-shortcuts{ display:grid; grid-template-columns:1fr 1fr; gap:8px; }
.home-sc      { display:flex; align-items:center; gap:10px; padding:12px; }
/* PC에서는 @media(min-width:900px) 의 4열/3열 그리드가 우선 적용 */
```

#### 문제 2: D+ 타 기기 미연동

**원인**: D+ 시작일을 `localStorage`에만 저장 → 다른 브라우저·기기에서 공유 불가

**해결**: Firestore `pjt_settings/{p4ph2|p4ph4}` 컬렉션에 동시 저장

```js
// saveStartDate() 수정
function saveStartDate(v){
  localStorage.setItem('fab_pjt_start_date', v);
  setDoc(doc(db,'pjt_settings','p4ph2'), {startDate:v, updatedAt:serverTimestamp()}, {merge:true});
  renderHome();
}
```

**앱 시작 시 Firestore → localStorage 동기화**:
```js
// waitForFirebaseAndInit() 이후 실행
getDoc(doc(db,'pjt_settings','p4ph2')).then(snap => {
  if(snap.exists() && snap.data().startDate !== localStorage값) {
    localStorage 갱신 + 화면 반영
  }
});
```

---

## Firestore 스키마 추가

```js
pjt_settings/{pjtKey}:   // pjtKey = 'p4ph2' | 'p4ph4'
{
  startDate:  string,     // 'YYYY-MM-DD'
  updatedAt:  serverTimestamp
}
```

---

## 이슈 & 해결

| 이슈 | 원인 | 해결 |
|------|------|------|
| `textContent` 설정 시 자식 DOM 삭제 | textContent 할당이 모든 자식 노드 교체 | 날짜 텍스트 div와 hidden input을 형제로 분리 |
| `showPicker()` 미작동 | 오늘 탭 날짜가 `getViewDate()`로 관리되는데 `viewDate` 사용 | `getViewDate()` 사용으로 교체 |
| 포털 iframe 내 그래픽 깨짐 | 홈탭 CSS 전체가 PC @media 전용 | 모바일 기본값 CSS 추가 |
| D+ 타 기기 미연동 | localStorage만 사용 | Firestore `pjt_settings` 저장/읽기로 전환 |
| via=portal 미전달 | overrideUrl 사용 시 파라미터 누락 | `(overrideUrl||m.url)+'?via=portal'` 방식으로 통일 |

---

## 2026-07-01 세션 — PJT 개편 (설정 탭 · 홈 하이브리드 · 실시간 반영)

> 버전: PJT 관리 **4.2.0 → 4.3.0** (MINOR, 기능 추가)
> 테섭(`portal-test`) 검증 완료 후 main 이식

### 신규/변경 기능

| 코드 | 파일 | 내용 |
|------|------|------|
| P1 | pjt·ph4 | **⚙️ 설정 탭 신설** — 상단 탭바(PC/모바일)에 추가. 신규 PJT 등록 정보(명칭·현장·거래처·내용·품목·물량·시작일) 수정. 저장은 `pjt_settings/{key}` |
| P1 | pjt·ph4 | 홈 하단 "프로젝트 설정" 섹션 제거 (설정 탭으로 이동, 섹터별 공정율은 공정 탭에서 확인) |
| P2 | pjt·ph4 | **헤더 실시간 반영** — 설정 저장/페이지 로드 시 상단 헤더(명칭·부제=거래처·내용)를 `pjt_settings` 값으로 갱신 (`applyPjtHeader`). 값 없으면 하드코딩 유지 |
| P2 | portal | **사이드바·카드 메뉴명 실시간 반영** — 로그인 시 `pjt_settings` 읽어 `PJT_SUBTABS`의 name·desc 갱신 후 재렌더 (`syncPjtSubtabsFromSettings`) |
| P3 | portal | **홈 하이브리드 레이아웃** — 상단 축소 카드(공정율·D+·누적공수, 2열 grid) + 하단 타임라인 2단(전체 일정 / 업무지시·보고). 날짜 시간순, 오늘 노드 강조 |
| P4 | pjt·ph4 | **헤더 우측 누적공수 → 전체 누적**으로 변경 (공사 시작일~오늘 `worker_manday`/`ph4_manday` 합산). 홈 가운데 카드는 "이달 누적" 유지 |
| P5 | pjt·ph4 | **오늘 탭 날짜 이동 수정** — 달력에서 날짜 선택 시 `viewDayOffset` 갱신하도록 (기존엔 미사용 변수 `viewDate`에 대입해 이동 안 됨) |
| P6 | portal | 설정 폼 URL 필드 삭제 |
| P6 | portal | 개별 PJT 빈 화면 수정 — overrideUrl(개별 PJT) 진입 시 서브탭 key를 `&tab=`으로 넘기지 않음 + `switchTab` 폴백(`ALL_TABS` 밖이면 home) |
| P7 | portal | 홈 일정/보고 패널 "DB 연결 안 됨" 수정 — `window._db=db` 전역 노출 (module 블록. `loadPjtPanels`가 참조하나 미설정이었음) |
| P7 | portal | 업무지시·보고 목록에서 내용 없는 항목 미표시 (필터) |

### 이슈 & 해결

| 이슈 | 원인 | 해결 |
|------|------|------|
| 설정 저장 `serverTimestamp is not defined` | UI 함수가 일반 `<script>` 블록에 위치 — Firestore 심볼(`serverTimestamp`,`db`,`setDoc`,`getDoc`)은 `module` 블록에서만 import/선언 | Firestore 접근부를 module 블록 헬퍼(`window._savePjtSettingsData` 등)로 이동, UI 함수는 헬퍼 호출 |
| 헤더 우측 누적공수 0.0 | 헤더가 홈 카드와 동일하게 "이달 합계"(`_mandayCache`, 당월만 로드)를 참조 | 전체 누적 전용 계산 `window._updateTotalManday` 추가 (시작일~오늘 전체 조회) |
| 오늘 탭 달력 선택 시 이동 안 됨 | `pickTodayDate`가 렌더에 안 쓰이는 `viewDate`에 대입 | 선택 날짜↔오늘 일수차를 `viewDayOffset`에 반영 |
| 홈 카드 세로로 쌓임 | `repeat(auto-fit, minmax(300px,1fr))`가 컨테이너 폭 대비 커서 2열 실패 | `repeat(2, minmax(0,1fr))` 2열 고정 |
| 페이지 로드 시 헤더/시작일 미반영 | 로드 IIFE가 일반 블록에서 `getDoc(doc(db,...))` 직접 호출(죽은 코드) | `_loadPjtSettingsData` 헬퍼 기반으로 교체 |

### Main 이식 (2026-07-01)

| 파일 | 커밋 SHA |
|------|---------|
| `pjt/index.html` | `b0b7e5a5f3` |
| `pjt_ph4/index.html` | `43ddb41bea` |
| `index.html` (홈 하이브리드·메뉴반영·DB패널·빈항목) | `a613673755` |

- 테섭 검증 완료분만 이식. `index.html`은 TEST 배너 제거 + `portal-test/`→`portal/` 8건 치환 후 이식 (기능만 반영)
