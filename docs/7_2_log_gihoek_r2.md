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
| *(배포 대기)* | 2026-06-26 | D1 프로젝트 상세 잔금 칸 제거 + 미수금 용어 통일 |
| `dee18714` | 2026-06-27 | fix: 견적 수신처 client 스냅샷 contact 필드 누락 + contactDropdown disabled 개선 |
| `ca9410ef` | 2026-06-27 | fix: window.drawEstForm/drawSettleForm 전역 등록 — 담당자 드롭다운 재렌더 버그 완전 해결 |
| `2a353fb9` | 2026-06-27 | debug: drawEstForm console.log 임시 삽입 (원인 추적용, 즉시 제거) |
| `ca9410ef` | 2026-06-27 | cleanup: 디버그 console.log 제거 (정식 배포) |

---

## 주요 변경 상세

### 견적 담당자 버그 — 전체 디버깅 과정 (2026-06-27)

#### 증상
- 견적 작성 시 발행처/수신처를 변경해도 담당자 드롭다운이 갱신되지 않음
- 수신처를 다람이엔지로 변경해도 이전 업체(범양냉방) 담당자가 그대로 표시됨

#### 오진 1차 (dee18714)
- **잘못된 진단**: `client` 스냅샷에 `contact` 필드 누락 + `contactDropdown`이 contacts 없으면 `return ''`
- **수정**: client 스냅샷에 `contact` 추가, contacts 없어도 disabled 드롭다운 표시
- **결과**: 문제 미해결 — 근본 원인이 아니었음

#### 진짜 원인 (ca9410ef)

```
Uncaught ReferenceError: drawEstForm is not defined
at HTMLSelectElement.onchange
```

- 발행처/수신처 `<select onchange="...;drawEstForm()">` 인라인 onchange에서 `drawEstForm()` 호출
- `<script type="module">` 내부 함수는 전역 스코프 접근 불가 → `ReferenceError` 발생
- 재렌더 자체가 중단 → 담당자 드롭다운 갱신 안 됨

**수정 (533~534번 줄 추가)**
```js
window.drawEstForm    = function(){ drawEstForm(); };
window.drawSettleForm = function(){ drawSettleForm(); };
```

#### 브라우저 캐시 문제
- 코드 수정·배포 완료 후에도 증상 지속
- 원인: 브라우저가 구버전 캐시 로드 → 콘솔에서 동일 ReferenceError 확인
- 해결: **Ctrl+Shift+R** 강제 새로고침 후 정상 작동 확인

#### 테스트 결과
- Unit Test: 14/14 PASS
- Integration Test: 8/8 PASS
- Acceptance Test: 17/17 PASS
- Demonstration: BEFORE/AFTER 시각적 시연 완료

---

### 기획-1: 정산 목록 최신순 정렬
- 발행일 내림차순 → 같은 날 no 내림차순
- `(b.no||'').localeCompare(a.no||'')`

### 기획-2: 정산 미수 잔금 표시
- 정산 탭 상단 요약 2칸 → 3칸
- 미수 잔금 칸: 양수=빨강, 0이하=초록

### 기획-3: 프로젝트 상세 잔금 + 정산 내역
- pjtDetail 요약: 4칸 → 5칸 (견적/청구/지급/**잔금**/손익)
- 견적 내역 아래 정산 내역 섹션 신설

### 기획-4: 정산 완결 (`doneSettle / undoneSettle`)
- 신규 status: `'done'`
- 청구(invoice)에만 "✓ 완결" 버튼
- 잔금 0이면 "(권장)" 자동 표시
- 회계 연동: 완결된 청구만 매출 인식 (`status==='done'`)

### 기획-5: 견적 종결 (`closeEst / reopenEst`)
- 신규 status: `'closed'`
- 종결 견적 → 유효 집계 제외
- `isActive(e)` = `e.status!=='void' && e.status!=='closed'`

### 기획-C1: 미수금 재정의
- 구: 청구 누계 − 지급 누계
- 신: 청구 누계 − **완결된 청구 합계**
- 헬퍼: `pjtDone(pid)`, `pjtDue(pid)`

### 기획 홈 KPI 재렌더 수정
- 3개 onSnapshot이 홈에서 재렌더를 안 했던 문제
- 각 구독에 `else if(curTab==='home') renderPlanHome()` 추가

### 기획-홈-백: 기획 홈 뒤로가기 버튼 추가
- 대상: 프로젝트·거래처·견적·정산·회계 탭 (5개 전체)
- 버튼: `<button class="back" onclick="tab('home')">← 기획 홈</button>`

### 기획-D1: 프로젝트 상세 잔금 칸 제거 + 미수금 용어 통일 (배포 대기)
- `pjtDetail` 요약: 5칸 → 4칸 (잔금 칸 제거)
- 미수금 = 청구−수금(완결) 개념으로 용어 통일

---

## 이슈 & 해결

| 이슈 | 해결 |
|------|------|
| Firebase config messagingSenderId 0 추가로 Auth 오류 | 원본 11자리로 복원 |
| renderHome 템플릿 리터럴 내 백틱 중첩 → SyntaxError | DOM 직접 조작 방식으로 우회 |
| 직접 URL 접근 시 allowed_users 미존재로 접근 불가 | portal_users 기반으로 인증 통일 |
| 미수금 개념 혼용 (지급 vs 수금) | 완결=수금으로 정의 통일, 프로젝트 상세 잔금 칸 제거 |
| 견적 발행처/수신처 변경 시 담당자 드롭다운 갱신 안 됨 | `drawEstForm` module scope → `window.drawEstForm` 전역 등록으로 해결 |
| 정산 발신자/수신자 변경 시 담당자 드롭다운 갱신 안 됨 | 동일 원인 — `window.drawSettleForm` 전역 등록으로 함께 수정 |
| 코드 수정 후에도 증상 지속 | 브라우저 캐시 문제 — Ctrl+Shift+R 강제 새로고침으로 해결 |
