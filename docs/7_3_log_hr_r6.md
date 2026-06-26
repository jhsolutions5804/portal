# 7.3. 개발 로그 — 인사 앱

> `portal/hr/index.html` 변경 이력
> 최초 작성: 2026-06-26 · 최종 수정: 2026-06-27 · 작성: 춘식이(Claude)

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

---

## [fix2] md 기준 명부 전면 정합 (`a31763f1`, 2026-06-27)

### 배경
md 파일(`2_1_hr_roster_r4`)과 실제 배포 코드를 항목별 비교한 결과, 51개 점검 항목 중 다수가 구버전 코드로 남아있음을 확인. 명부 섹션 전면 재작성.

### 누락됐던 항목 (이번에 적용)

| 항목 | 이전 | 이후 |
|------|------|------|
| `portalUid` workers 저장 | ❌ | ✅ rosterSave에 명시 저장 |
| `signData` workers 저장 | ❌ | ✅ rosterSave null 초기화·rosterDetailSave 저장 |
| `➕ 신규 등록` 버튼 | ❌ 구버전 selectMain | ✅ 우측 상단 독립 버튼 |
| 포털 열 🔗/미연동 | ❌ | ✅ |
| portal_users 드롭다운 | ❌ | ✅ reg-portal-select |
| `rosterRegPortalSelect` | ❌ | ✅ |
| `rosterDetailSave` portal_users 역방향 동기화 | ❌ | ✅ name·rank·dept |
| `rosterEmpNoCancel` | ❌ | ✅ |
| `rosterEmpNoSave` empNo 역방향 동기화 | ❌ | ✅ portal_users.empNo |
| 신규 등록 시 portal_users.empNo 동기화 | ❌ | ✅ |
| 서명 패드 (rosterOpenSignPad 등) | ❌ | ✅ canvas 380×120 |
| `window.getWorkerData` | ❌ | ✅ 전역 등록 |
| `renderRosterList → renderRosterMain` | ❌ | ✅ |

### 유지된 항목
- `KR_HOLIDAYS` + `calcWorkDays` 위치 (rosterDetail 앞)
- 중첩 백틱 없음 (문자열 연결 방식 사용)
- 사번 자동 부여 (yy+padStart(3,'0'))
- `rosterDelete` confirm + deleteDoc

---

## 이슈 & 해결

| 이슈 | 원인 | 해결 |
|------|------|------|
| 상세 모달 열리지 않음 | modal.innerHTML 중첩 백틱 | 문자열 연결 방식으로 교체 |
| 재직기간 0 표시 | D3 교체 시 calcWorkDays 누락 | 원본 복원 |
| 대부분 기능 미반영 | D3 배포 시 old 코드가 섹션에 잔존 | fix2에서 md 기준 전면 재작성 |
