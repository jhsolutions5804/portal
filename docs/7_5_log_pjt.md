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
