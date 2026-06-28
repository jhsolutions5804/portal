# 7.3. 개발 로그 — 인사 앱 (r9)

> `portal/hr/index.html` 변경 이력
> 최초 작성: 2026-06-26 · 최종 수정: 2026-06-29(r9) · 작성: 춘식이(Claude)

---

## 커밋 이력

| SHA | 날짜 | 내용 |
|-----|------|------|
| *(초기)* | 2026-06-24 | 7개 탭 구성 |
| `668d253f` | 2026-06-27 | [D1] hr 내부 사이드바 제거 |
| `6c236d60` | 2026-06-27 | [D2] 명부 PC 레이아웃 + portal_users 드롭다운 |
| `755521e6` | 2026-06-27 | [D3] 명부 v3 전면 개선 |
| `4037f6e3` | 2026-06-27 | [fix1] modal 중첩 백틱 + calcWorkDays 복원 |
| `a31763f1` | 2026-06-27 | [fix2] md 기준 명부 전면 정합 |
| `9b9f4abc` | 2026-06-27 | [E1] 연봉계약서 PC 테이블 레이아웃, 사원번호 순 정렬 |
| `620abd6c` | 2026-06-27 | [D4] getWorkersList empNo 단일 정렬 통일 |
| `3c9b1942` | 2026-06-27 | [D3] 근로계약서 PC 테이블 재배포 |
| `d88ee9b4` | 2026-06-27 | [F1] 초과근로 PC 레이아웃 복구 |
| `fd0e3313` | 2026-06-27 | 포털 전용 접근 — denied 차단 화면 |
| `d00296de` | 2026-06-27 | [G1] 급여명세서 PC 레이아웃 |
| `e8c25e53` | 2026-06-29 | [RT-PC] 퇴직금 정산 PC 레이아웃 전환 |

---

## [RT-PC] 퇴직금 정산 PC 레이아웃 전환 (`e8c25e53`, 2026-06-29)

### 배경
기존 퇴직금 정산 탭이 `wrap2()` / `card2()` 기반 모바일 카드 UI로만 구현되어 있어, 다른 HR 탭(초과근로, 급여명세서 등)과 일관성이 없었음. PC 환경에서 공간 낭비가 심해 레이아웃 개선 요청.

### 변경 내용

**PC 뷰 (`window.innerWidth >= 900`)**
- 기존 단계별 이동(메인 → 산정화면 → 결과) 방식 제거
- 좌우 분할 레이아웃으로 전환:
  - 좌측 280px: 산정 조건(근로자·퇴직일) + 정산 내역 목록 + 주의문구
  - 우측 flex:1: 계산 결과 (2열 그리드: 평균임금 테이블 / 재직기간·산식·퇴직금)
- 근로자·퇴직일 변경 시 즉시 계산 (`onchange` 트리거)
- 저장 후 페이지 전환 없이 좌측 내역 패널만 갱신

**모바일 뷰 (`window.innerWidth < 900`)**
- 기존 카드 UI 완전 유지 (`renderRetireMobile`, `renderRetireCalcMobile`)
- `renderRetireCalc` alias 유지 (기존 호출 호환)

**신규 함수**
- `renderRetirePC()` — PC 뷰 뼈대
- `renderRetireMobile()` — 모바일 메인 (구 `renderRetireMain` 내용)
- `renderRetireCalcMobile()` — 모바일 산정 (구 `renderRetireCalc` 내용)
- `rtLoadListPanel(wid, panel)` — PC 좌측 내역 패널 비동기 로드
- `rtDeleteFromPanel(wid, rid)` — PC 내역 패널 삭제

**계산 로직 (`retireCompute`)**: 변경 없음. PC/모바일 결과 렌더 분기만 추가.

### 이슈 & 해결

| 이슈 | 원인 | 해결 |
|------|------|------|
| 없음 | — | JS 문법 `node --check` 1회 통과, 목업 데모 정상 확인 후 배포 |

### 백업
- `backup/hr_index_backup_v1.0.2_20260629.html`
- `/home/claude/rollback/hr_index_backup_v1.0.2_20260629.html`
