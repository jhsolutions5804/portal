# 7.2. 개발 로그 — 기획 앱

> `portal/gihoek/index.html` 변경 이력
> 최초 작성: 2026-06-26 · 최종 수정: 2026-06-29 · 작성: 춘식이(Claude)

---

## 커밋 이력

| SHA | 날짜 | 내용 |
|-----|------|------|
| *(초기)* | 2026-06-24 | 5개 탭: 홈·프로젝트·거래처·견적·정산 |
| `99209c5f` | 2026-06-26 | 기획 홈 KPI 재렌더 (홈 탭 onSnapshot 연결) |
| `9ab8f6645` | 2026-06-26 | 정산 최신순 정렬 + 미수 잔금 칸 + 프로젝트 정산내역 |
| `d4aa3165` | 2026-06-26 | 정산 완결(done) + 견적 종결(closed) + 회계 완결만 매출 |
| `7916507071` | 2026-06-26 | 기획 홈 KPI planShowList 팝업 |
| `2a9910615b` | 2026-06-26 | C1 미수금 재정의 (청구−완결) |
| `d59a156d81` | 2026-06-26 | 기획 홈 뒤로가기 버튼 추가 (5개 탭 전체) |
| *(미확인SHA)* | 2026-06-26 | D1 프로젝트 상세 잔금 칸 제거 + 미수금 용어 통일 |
| `dee18714` | 2026-06-27 | fix: 견적 수신처 client 스냅샷 contact 필드 누락 + contactDropdown disabled 개선 |
| `ca9410ef` | 2026-06-27 | fix: window.drawEstForm/drawSettleForm 전역 등록 — 담당자 드롭다운 재렌더 버그 완전 해결 |
| `2a353fb9` | 2026-06-27 | debug: drawEstForm console.log 임시 삽입 (원인 추적용, 즉시 제거) |
| `ed45c239` | 2026-06-27 | feat: 견적 작성 폼 작성자 섹션 제거 + 출력 stamp 발행처 담당자 표시 |
| `bebb8221` | 2026-06-27 | feat: 견적·정산 stamp 담당자 연락처·메일 추가 (ctSnap 헬퍼 신규) |
| `245a8b8f` | 2026-06-27 | fix: ctSnap 공통 함수로 승격 — saveEst 개정 발행 ReferenceError 수정 |
| `56834f65` | 2026-06-29 | fix: 기획 앱 중복 헤더(📊 기획 타이틀) 제거 |

---

## 주요 변경 상세

### 중복 헤더 제거 (2026-06-29, 56834f65)

**증상**: 포털 상단에 "기획" 텍스트가 표시되는데, 앱 내부 `.head` 영역에도 동일하게 📊 아이콘 + "기획" h1 타이틀이 중복 표시됨

**원인**: `gihoek/index.html` `.head` 내부에 `<div class="t"><div class="ic">📊</div><h1>기획</h1></div>` 존재. 포털 iframe 내에서는 포털 헤더가 이미 현재 앱명을 표시하므로 불필요.

**수정**
- HTML: `.head > .t` 블록 (아이콘+h1) 제거
- CSS: `.head .t`, `.head .t h1`, `.head .t .ic` 스타일 3줄 제거

---

### 견적 개정 발행 ReferenceError 수정 (2026-06-27, 245a8b8f)

**원인**: `ctSnap`이 `saveSettle` 내부 지역 함수로만 존재하는데, `saveEst`에서 외부 참조하여 에러 발생

**수정**: `ctSnap`을 모듈 스코프 공통 함수로 승격, `saveSettle` 내부 지역 `ctSnap` 제거

```js
function ctSnap(cid, name){
  const c = compById(cid);
  const ct = (c?.contacts||[]).find(x=>x.name===name)||{};
  return {contact:name||'', contactTel:ct.tel||'', contactEmail:ct.email||''};
}
```

---

### 견적 담당자 드롭다운 버그 (2026-06-27, ca9410ef)

- 원인: `drawEstForm` module scope 함수 → 인라인 onchange ReferenceError
- 수정: `window.drawEstForm`, `window.drawSettleForm` 전역 등록

---

## 이슈 & 해결

| 이슈 | 해결 |
|------|------|
| 견적 발행처/수신처 변경 시 담당자 드롭다운 갱신 안 됨 | `window.drawEstForm` 전역 등록 |
| 코드 수정 후에도 증상 지속 | 브라우저 캐시 → Ctrl+Shift+R |
| 견적 개정 발행(saveEst) ReferenceError | `ctSnap` 지역함수 → 공통 함수로 승격 |
| 견적서 stamp 작성자 불필요 표시 | stamp 작성자 섹션 제거 |
| 견적서 stamp 발행처 담당자 미표시 | `iss.contact` stamp 추가 |
| 포털 내 기획 앱 헤더 중복 표시 | `.head .t` 블록 및 관련 CSS 제거 |
