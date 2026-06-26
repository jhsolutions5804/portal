# 7.2. 개발 로그 — 기획 앱

> `portal/gihoek/index.html` 변경 이력
> 최초 작성: 2026-06-26 · 최종 수정: 2026-06-27 · 작성: 춘식이(Claude)

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
| *(미확인SHA)* | 2026-06-26 | D1 프로젝트 상세 잔금 칸 제거 + 미수금 용어 통일 (배포 완료 확인) |
| `dee18714` | 2026-06-27 | fix: 견적 수신처 client 스냅샷 contact 필드 누락 + contactDropdown disabled 개선 |
| `ca9410ef` | 2026-06-27 | fix: window.drawEstForm/drawSettleForm 전역 등록 — 담당자 드롭다운 재렌더 버그 완전 해결 |
| `2a353fb9` | 2026-06-27 | debug: drawEstForm console.log 임시 삽입 (원인 추적용, 즉시 제거) |
| `ed45c239` | 2026-06-27 | feat: 견적 작성 폼 작성자 섹션 제거 + 출력 stamp 발행처 담당자 표시 |
| `bebb8221` | 2026-06-27 | feat: 견적·정산 stamp 담당자 연락처·메일 추가 (ctSnap 헬퍼 신규) |
| `245a8b8f` | 2026-06-27 | fix: ctSnap 공통 함수로 승격 — saveEst 개정 발행 ReferenceError 수정 |

---

## 주요 변경 상세

### 견적 개정 발행 ReferenceError 수정 (2026-06-27, 245a8b8f)

**증상**: EST-2026-008 수정(개정) 발행 클릭 시 저장 실패

**원인**
```
saveSettle() {
  const ctSnap = (cid,name) => { ... }  ← 지역 함수로만 정의
}
saveEst() {
  ...ctSnap(d.clientId, d.clientContact)  ← saveSettle 밖에서 호출
  // → ReferenceError: ctSnap is not defined
}
```
`ctSnap`이 `saveSettle` 내부 지역 함수로만 존재하는데, `saveEst`에서 외부 참조하여 에러 발생. 신규 견적 저장도 동일하게 실패했으나 개정 발행 시 더 명확히 인지된 케이스.

**수정**
- `ctSnap`을 모듈 스코프 공통 함수로 승격 (560~561번 줄)
- `saveSettle` 내부 지역 `ctSnap` 제거 (중복 제거)

```js
// 수정 후 — 모듈 스코프 공통 함수
function ctSnap(cid, name){
  const c = compById(cid);
  const ct = (c?.contacts||[]).find(x=>x.name===name)||{};
  return {contact:name||'', contactTel:ct.tel||'', contactEmail:ct.email||''};
}
```

**테스트**
- Unit Test: 7/7 PASS
- Integration Test: 7/7 PASS (EST-2026-008 개정 발행 시나리오 포함)

---

### 견적 작성 폼 작성자 섹션 제거 + stamp 담당자 표시 (2026-06-27, ed45c239)

- 폼에서 소속부서·이름·메일주소·작성자명 4개 입력란 제거
- stamp: 작성자 줄 제거 → 발행처 담당자(`iss.contact`) 표시 추가

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
