# 7.2. 개발 로그 — 기획 앱

> `portal/gihoek/index.html` 변경 이력
> 최초 작성: 2026-06-26 · 작성: 춘식이(Claude)

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

---

## 주요 변경 상세

### 견적 담당자 버그 최종 수정 (2026-06-27)

**진짜 원인: window.drawEstForm 전역 미등록**

- 발행처/수신처 `<select onchange="...;drawEstForm()">` 에서 인라인 onchange가 `drawEstForm()`을 호출
- `<script type="module">` 내부 함수는 전역 접근 불가 → `ReferenceError` → 재렌더 중단
- 담당자 드롭다운이 업체 변경 후 갱신되지 않던 근본 원인

**수정 내용 (533~534번 줄 추가)**
```js
window.drawEstForm   = function(){ drawEstForm(); };
window.drawSettleForm = function(){ drawSettleForm(); };
```

**이전 수정(dee18714)과의 관계**
- `dee18714`: client 스냅샷 contact 누락 + contactDropdown disabled 개선 → 부분 수정
- `ca9410ef`: drawEstForm 전역 등록 → 재렌더 정상화 → 담당자 드롭다운 완전 해결

**테스트 결과**
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
- 각 탭 렌더 함수(`renderPjt`, `renderComp`, `renderEst`, `renderSettle`, `renderAcct`) 최상단에 추가
- 버튼: `<button class="back" onclick="tab('home')">← 기획 홈</button>`
- 기존 `.back` 스타일 그대로 활용, `tab('home')` 호출로 상태 초기화 + 홈 복귀

### 기획-D1: 프로젝트 상세 잔금 칸 제거 + 미수금 용어 통일 (배포 대기)

**변경 이유**
- 프로젝트 상세 요약의 "미수 잔금"이 `청구−지급` 기준이었으나, 실제 미수금은 `청구−수금(완결)` 기준이어야 함
- 완결 처리된 대금청구서 = 수금 완료로 간주하는 개념 정립
- 중복 표시 제거: 미수금은 정산 탭 상단 요약에서만 표시

**수정 내용**
1. `pjtDetail` 요약: 5칸(견적/청구/지급/잔금/손익) → **4칸(견적/청구/지급/손익)**, 잔금 칸 제거
2. 정산 탭 상단 요약 라벨: `미수 잔금 (청구−완결)` → `미수금 (청구−수금)`
3. 헬퍼 주석: `완결된 청구서 합계` → `수금액(완결 청구 = 수금으로 간주)`
4. 완결 확인 메시지: `미수 잔금` → `미수금`, "완결 시 수금 처리되어 회계 매출로 인식됩니다"로 표현 강화

---

## 이슈 & 해결

| 이슈 | 해결 |
|------|------|
| Firebase config messagingSenderId 0 추가로 Auth 오류 | 원본 11자리로 복원 |
| renderHome 템플릿 리터럴 내 백틱 중첩 → SyntaxError | DOM 직접 조작 방식으로 우회 |
| 직접 URL 접근 시 allowed_users 미존재로 접근 불가 | portal_users 기반으로 인증 통일 |
| 미수금 개념 혼용 (지급 vs 수금) | 완결=수금으로 정의 통일, 프로젝트 상세 잔금 칸 제거 |
| 견적 발행처/수신처 변경 시 담당자 드롭다운 갱신 안 됨 | `drawEstForm`이 module scope 함수라 인라인 onchange에서 `ReferenceError` → `window.drawEstForm` 전역 등록으로 해결 |
| 정산 발신자/수신자 변경 시 담당자 드롭다운 갱신 안 됨 | 동일 원인 — `window.drawSettleForm` 전역 등록으로 함께 수정 |
