# 7.3. 개발 로그 — 인사 앱 (r9b)

> `portal/hr/index.html` 변경 이력 (후반부 / r9a에서 이어짐)
> 최초 작성: 2026-06-26 · 최종 수정: 2026-06-29(r9b) · 작성: 춘식이(Claude)

---

## r7 이후 누락 커밋 보완 (`620abd6c` ~ `fd0e3313`, 2026-06-27)

### [D4] getWorkersList empNo 단일 정렬 (`620abd6c`)
- 기존: `name` 기준 sort가 `empNo` sort를 덮어쓰는 버그 존재
- 수정: `getWorkersList` 내 `empNo` localeCompare 단일 정렬로 통일

### [D3] 근로계약서 PC 테이블 재배포 (`3c9b1942`)
- `renderLaborMain` 진입 시 바로 근로자 목록 테이블 표시
- 신규 작성·조회 버튼 상단 배치

### [F1] 초과근로 PC 레이아웃 복구 (`d88ee9b4`)
- `innerWidth >= 900` 분기 — `renderOvertimePC` / `renderOvertimeMobile`
- PC: KPI 바(4열) + 좌패널(직원목록·입력폼) + 우패널(상세내역)

### 포털 전용 접근 (`fd0e3313`)
- Firebase Auth 유지, `portal_users` 컬렉션 권한 확인
- 미등록 사용자 → `denied-card` 차단 화면 표시

---

## 급여명세서 PC 레이아웃 (G1, `d00296de`, 2026-06-27)

### 변경 내용

**PC/모바일 분기 (`PS_PC_BP = 900`)**

| 항목 | Before | After |
|------|--------|-------|
| 진입 | 작성/조회 카드 선택 (`selectMain`) | PC: 바로 작성 화면 / 모바일: 기존 유지 |
| 작성 레이아웃 | 단일 컬럼 카드 스택 | 좌(260px) + 우(flex:1) 2단 |
| 지급/공제 표시 | 순차 카드 | 좌우 **2열 grid** 동시 표시 |
| 조회 레이아웃 | 근로자 목록 → 월 목록 2단계 탐색 | 좌(240px) + 우 카드 그리드 1단계 |

**신규 함수**

| 함수 | 역할 |
|------|------|
| `renderPayslipPC()` | PC 작성 뼈대 + 핸들러 등록 |
| `renderPayslipPCRight()` | PC 우패널 계산값 렌더 (재호출용) |
| `renderPayslipPCList()` | PC 조회 뼈대 |
| `psLoadWorkerSlips(wid, wname, btn)` | PC 조회 우패널 월별 카드 로드 |
| `psDeleteSlipPC(wid, mid, wname)` | PC 삭제 후 우패널 갱신 |
| `psPcMonthChange(month)` | 기준월 변경 → 초과근로 재연동 |
| `psPcWorkerSelect(wid)` | 근로자 선택 → 연봉계약서 로드 |

**모바일 기존 함수 완전 유지**
- `renderPayslipWrite`, `renderPayslipWriteForm`, `renderPayslipListNew`,
  `psWorkerSelect`, `psViewWorker`, `psViewDetail`, `psDeleteSlip`

### 이슈 & 해결

| 이슈 | 원인 | 해결 |
|------|------|------|
| PC 레이아웃 미표시 | `tab-content`가 `display:block`이라 `height:100%;flex:1` 방식 부모 높이 없음 | `max-width:1100px;margin:0 auto` 스크롤 방식으로 전환 (초과근로 동일 패턴) |
| `calcPayDateGlobal` 코드 파손 | str_replace 범위 지정 미스로 함수 본문이 `psDeleteSlipPC` 안에 삽입됨 | 파일을 3분할(head/새코드/tail) 후 재합산 |


---

## 포털 전용 인증 전환 (D3, `fd0e3313`, 2026-06-29)

- Firebase Auth 완전 제거, `?via=portal` 파라미터 유무로만 접근 판단
- 직접 접근 시 `blocked-screen` 표시
- 포털(`portal/index.html`)에서 권한 일원화

| 이슈 | 원인 | 해결 |
|------|------|------|
| `?via=portal` 있어도 blocked 표시 | `type="module"` IIFE에서 일반 `<script>` 함수 참조 불가 | 인증 IIFE를 일반 `<script>` 안으로 이동 |
| 포털에서도 blocked 표시 | MODULES url에 `?via=portal` 포함 + `openModule`이 재추가 → 이중 파라미터 | MODULES url에서 `?via=portal` 제거 (D4) |

---

## 인사 홈 버튼 (G1, `0cf4fed4`, 2026-06-29)

- `homeBtn()` 헬퍼 함수 추가 (회색 박스 버튼)
- 7개 탭 메인 화면 좌측 상단 일괄 적용 → `goTab('home')` 호출

---

## PC 레이아웃 복구 (H2·I1·I2, 2026-06-29)

| 커밋 | 내용 |
|------|------|
| `49c27f03` | 급여명세서 PC 레이아웃 (`PS_PC_BP=900`, 작성·조회 분리) |
| `d7b26a01` | 근로자 명부·근로계약서·연봉계약서·퇴직금 커밋 이력에서 복구 |
| `de66ce72` | `_loadRosterDocs` 누락 복원, homeBtn 재삽입, 연차현황 수정버튼 복구 |

| 이슈 | 원인 | 해결 |
|------|------|------|
| `_loadRosterDocs is not defined` | 커밋 함수 교체 시 의존 함수 누락 | a31763f1에서 추출 후 재삽입 |
| homeBtn 사라짐 | G1 이전 커밋 기준 함수로 교체 | 헤더 위치에 직접 삽입 |
| 연차현황 수정버튼 누락 | 다른 대화 배포본(c142acb8)이 반영 안 됨 | c142acb8에서 추출 후 교체 |
| homeBtn 중복 삽입 | replace 중복 적용 | 중복 div 제거 |