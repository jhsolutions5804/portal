# Backup Log

## v1.0.4 — 2026-06-29

### 백업 파일
| 파일 | SHA |
|------|-----|
| portal/index.html    | 15000739 |
| hr/index.html        | 67dcd9e9 |
| gihoek/index.html    | cc0b9ce5 |
| outlook-auth.html    | 03b04c26 |

### 주요 변경 내용 (v1.0.3 → v1.0.4)
- J3: 연차현황 `_isAdmin` 파라미터 수신
- J4: 퇴직금 드롭박스 `empNo` 정렬
- J5: 퇴직금 `rt-list-panel` 저장 내역 연동
- J6: 기획/인사 좌우 여백 `1100px` 통일
- J2: gihoek 홈 버튼 `.home-back` 통일
- J1: 루트 md 파일 `docs/` 정리
- K1: 급여명세서 지급계·실지급액 오류 수정
- K2: 전체 드롭박스 `empNo` 정렬 통일
- K3: Outlook MSAL → OAuth2 PKCE 직접 구현
- L2: 근로자 명부 → portal_users 역방향 연동
- L3: 근로자 명부 수정 저장 `oninput` 오류 수정
- hotfix: renderOutlookCard 함수 복구

---
# Backup Log — hr/index.html

> 백업 대상: `portal/hr/index.html`
> 저장 위치: GitHub `backup/` + local `/home/claude/rollback/`
> 파일명 규칙: `hr_index_backup_v{major}.{minor}.{patch}_{yyyymmdd}.html`
> 최초 작성: 2026-06-27 · 작성: 춘식이(Claude)

---

## 버전 체계

| 자리 | 의미 | 증가 조건 |
|------|------|-----------|
| major | 대규모 구조 변경 | 앱 전체 재설계, 탭 구조 변경 등 |
| minor | 기능 단위 추가/변경 | 신규 탭, PC 레이아웃 추가 등 |
| patch | 버그 수정 / 소규모 개선 | 오류 수정, 스타일 조정 등 |

---

## 백업 이력

### v1.0.0 — 2026-06-27

| 항목 | 내용 |
|------|------|
| 파일명 | `hr_index_backup_v1.0.0_20260627.html` |
| 기준 커밋 | `d00296de` |
| 백업 시점 | 급여명세서 PC 레이아웃 완료 + 문서(r2) + 로그(r8) 업로드 완료 |

**포함된 주요 기능 (이 버전 기준 전체 상태)**

| 탭 | 상태 | 비고 |
|----|------|------|
| 인사 홈 | ✅ | KPI 카드, 이달 현황 |
| 근로자 명부 | ✅ | PC 테이블, 서명패드, portal_users 연동 |
| 근로계약서 | ✅ | PC 테이블, 신규작성/조회 버튼 |
| 연봉계약서 | ✅ | PC 테이블, 사번 정렬, 상태 표시 |
| 초과근로 | ✅ | PC 좌우패널, KPI 바 |
| 급여명세서 | ✅ | PC 좌우패널 + 2열 지급/공제, 조회 카드뷰 |
| 퇴직금 정산 | ✅ | |
| 연차 현황 | ✅ | |

**이번 배포에서 추가된 내용 (v1.0.0 직전 커밋)**
- `PS_PC_BP = 900` 분기
- `renderPayslipPC` — 좌(260px 선택패널) + 우(2열 지급/공제 grid) 레이아웃
- `renderPayslipPCRight` — 우패널 계산값 재렌더 함수
- `renderPayslipPCList` — PC 조회 화면 (좌: 근로자 목록, 우: 카드 그리드)
- `psLoadWorkerSlips`, `psDeleteSlipPC`, `psPcMonthChange`, `psPcWorkerSelect`
- 모바일 기존 함수 완전 유지
- `tab-content` height 제약 문제 → `max-width:1100px; margin:0 auto` 스크롤 방식으로 해결

---

*(다음 백업 시 이 파일에 추가)*
