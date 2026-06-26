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

---

## 주요 변경 상세

### 견적 작성 폼 작성자 섹션 제거 + stamp 담당자 표시 (2026-06-27, ed45c239)

**배경**: 견적서 출력 시 불필요한 작성자 정보(소속부서·이름·이메일)가 표시되고,
발행처 담당자는 나오지 않는 문제 개선 요청.

**수정 1 — 견적 작성 폼 (drawEstForm)**
- 제거 항목: 소속부서 / 이름 / 메일주소 / 작성자명 입력란 4개
- `authorUid`(로그인 uid)는 계속 `saveEst` payload에 저장
- `authorDept`, `authorName`, `authorEmail`은 빈값으로 저장됨 (하위 호환 유지)

**수정 2 — 견적서 출력 stamp (printEst)**
```js
// 수정 전
위와 같이 견적합니다.
[작성자: 소속부서 이름  이메일]   ← 제거
[발행처 회사명]  대표 [대표자] (인)

// 수정 후
위와 같이 견적합니다.

[발행처 회사명]  대표 [대표자] (인)
담당: [issuerContact]              ← 신규 (담당자 선택 시만 표시)
```

**테스트 결과**
- Unit Test: 14/14 PASS
- Integration Test: 12/12 PASS
- Acceptance Test: 15/15 PASS
- Demonstration: BEFORE/AFTER 시각적 시연 완료

---

### 견적 담당자 버그 — 전체 디버깅 과정 (2026-06-27)

**증상**: 발행처/수신처 변경 시 담당자 드롭다운 미갱신

**오진 1차 (dee18714)**: client 스냅샷 contact 누락 + contactDropdown return '' 문제로 오판 → 부분 수정만 됨

**진짜 원인 (ca9410ef)**: `drawEstForm`이 `<script type="module">` 내부 함수 → 인라인 onchange에서 `ReferenceError` → 재렌더 중단

```js
window.drawEstForm    = function(){ drawEstForm(); };
window.drawSettleForm = function(){ drawSettleForm(); };
```

**브라우저 캐시**: 배포 후에도 증상 지속 → Ctrl+Shift+R 강제 새로고침으로 해결

---

### 기타 변경 (2026-06-26)

- 정산 목록 최신순 정렬 / 미수 잔금 표시 / 프로젝트 상세 정산 내역
- 정산 완결(done) / 견적 종결(closed) / 회계 완결만 매출
- 기획 홈 KPI 팝업 / 미수금 재정의 / 뒤로가기 버튼

---

## 이슈 & 해결

| 이슈 | 해결 |
|------|------|
| Firebase config messagingSenderId 0 추가로 Auth 오류 | 원본 11자리로 복원 |
| 견적 발행처/수신처 변경 시 담당자 드롭다운 갱신 안 됨 | `window.drawEstForm` 전역 등록 |
| 정산 발신자/수신자 변경 시 담당자 드롭다운 갱신 안 됨 | `window.drawSettleForm` 전역 등록 |
| 코드 수정 후에도 증상 지속 | 브라우저 캐시 → Ctrl+Shift+R |
| 견적서 출력 stamp에 작성자 정보 불필요하게 표시 | stamp에서 작성자 섹션 제거 |
| 견적서 출력에 발행처 담당자 미표시 | stamp에 `iss.contact` 추가 |
