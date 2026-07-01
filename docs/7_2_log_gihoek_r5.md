# 7.2. 개발 로그 — 기획 앱

> `portal/gihoek/index.html` 변경 이력
> 최초 작성: 2026-06-26 · 최종 수정: 2026-06-29(r5) · 최종 수정: 2026-06-27 · 작성: 춘식이(Claude)

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
| `70082f5a` | 2026-06-29 | [H1] 기획 홈 버튼 → 인사 스타일(home-back) 통일 |
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


---

## 기획 홈 버튼 스타일 통일 (H1, `70082f5a`, 2026-06-29)

- "← 기획 홈" `.back` 텍스트 버튼 → `.home-back` 박스 버튼으로 교체
- 인사 섹션 `homeBtn()` 스타일과 통일 (`🏠 기획 홈`, 회색 박스)
- "← 목록", "← 뒤로" 등 탭 내 뒤로가기 버튼은 `.back` 그대로 유지
- 적용 탭: 프로젝트·거래처·견적·정산·회계 (5개)
---

## 급여·용역비 직접비 자동연동 (N10-1/N10-2, 2026-06-30~07-01)

> Test server에서 무결점 테스트 후 main 이식 완료

### 커밋 이력 (main)
| SHA | 내용 |
|-----|------|
| `beefbb1c` | N10-1/N10-2 일괄 이식 (test 검증본) |

### N10-1 — 하청 용역비 자동연동
- 지급예정서(`docType:'payment'`)에 "✓ 지급완료" 버튼 추가 (`doneSettlePayment`). 기존 완결(invoice 전용)과 분리, 라벨/메시지 분기
- 비용장부가 완결된 지급예정서를 자동 집계: `paymentAsExpense()`가 `status==='done' && baseMonth===현재회계월` 인 payment를 cat:'용역비'(직접비) 가상비용으로 변환
- `accMonthExp()` = 수동입력 expenses + paymentAsExpense() → 손익/카테고리집계/PJT별 직접비 모두 자동 반영
- 자동반영 항목은 "🔗 정산 연동" 태그 표시, 클릭 시 정산서로 이동(수정 불가). 지급완료 취소 시 자동 제외

### N10-2 — 급여 PJT 비율배분
- 회계>비용장부에 "👥 급여 배분" 버튼. 접근B(gihoek 입력) + 급여명세서 자동로드
- 흐름: 근로자 선택(`workers` 컬렉션) → `salLoadMonths`로 그 직원의 발행된 명세서 월 목록(`payslips/{wid}/months` getDocs, 최신순) → 월 선택 시 `salLoadNet`로 **netPay(실지급액)** 로드
- **기준금액 = netPay** (세전 grossPay 아님)
- **급여일 지정**: `defaultPayDate(기준월)` = 익월 말일, 주말이면 직전 평일(금)로 당김. date 입력칸으로 공휴일 등 직접 수정 가능. 회계 반영월 = 급여일이 속한 월
- PJT별 비율% → 금액 실시간 계산(100% 초과 차단). 저장 시 동일 직원·기준월 기존 salaryDist 항목 전체 삭제 후 재작성 (id: `salary_{wid}_{기준월}_{pjt}`, cat:'급여', salaryDist:true). "👥 급여배분" 태그

### 데이터 구조
- `gihoek_expenses` 급여배분 항목: `{date:급여일, cat:'급여', vendor:이름, total:배분액, pjt, salaryDist:true, workerId, salBaseMonth:기준월, baseMonth:반영월}`
- 직접비(DIRECT_CATS): ['급여','용역비','공구·자재비']
- 급여명세서 읽기: `payslips/{workerId}/months/{month}` (필드: netPay, grossPay 등). 직원: `workers` 컬렉션

### 이슈 & 해결
| 이슈 | 해결 |
|------|------|
| 재입력 시 PJT 개수 감소하면 빠진 PJT 항목 잔존 | 저장 전 동일 직원·기준월 salaryDist 항목 전체 삭제 후 재작성 |
| 급여배분 버튼 안 보임 | iframe 캐시 문제 (코드 정상). 근본해결 N11 |

---

## 2026-07-01 세션 — 지급예정서 회계 계상월 자동화

> 버전: 정산 **1.4.x → MINOR +1** (기능 추가)

### 변경 내용

| 코드 | 내용 |
|------|------|
| G1 | 지급예정서(payment) 회계 계상월을 급여와 동일 규칙 적용 — 지급예정일(payDate) 기준 |
| G1 | 지급예정일 비면 `defaultPayDate(기준월)` = 익월 말일(주말→금요일 보정) 자동 |
| G1 | `acctMonthOf(s)` 헬퍼 — 저장된 `acctMonth` 우선, 없으면 payDate→issueDate→baseMonth 폴백(하위호환) |
| G1 | 발행 시 `acctMonth` 저장, 상세보기에 회계 계상월 표시 + 수정 버튼(`editAcctMonth`, prompt YYYY-MM) |
| G1 | `paymentAsExpense` 필터를 `baseMonth` → `acctMonth` 기준으로 변경 |

### Main 이식
- `gihoek/index.html` 커밋 `45e36db07f` — test 전용 요소 없어 그대로 이식
