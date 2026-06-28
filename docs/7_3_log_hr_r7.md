# 7.3. 개발 로그 — 인사 앱

> `portal/hr/index.html` 변경 이력
> 최초 작성: 2026-06-26 · 최종 수정: 2026-06-27(r7) · 작성: 춘식이(Claude)

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

---

## 연봉계약서 개편 (E1, `9b9f4abc`, 2026-06-27)

### 변경 내용

**1. renderAnnualMain — PC 테이블 레이아웃**

| 항목 | Before | After |
|------|--------|-------|
| 진입 화면 | 등록/조회 카드 선택 (`selectMain`) | PC 테이블 직접 표시 |
| max-width | 840px (`wrap2`) | 1100px (근로계약서 동일) |
| 신규 작성 | 카드 클릭 | 우측 상단 ➕ 버튼 |
| 상세 진입 | 별도 목록 → 선택 2단계 | 이름 클릭 or 조회 버튼 1단계 |
| 컬럼 | — | 사원번호·이름·소속·직급·구분·최신계약일·계약수·상태·조회 |

**2. 사원번호 순 정렬**
- `workers` 배열 `empNo` 기준 `localeCompare` 정렬 후 렌더링

**3. renderAnnualList2 래퍼 통합**
- 기존 `renderAnnualList2` (별도 조회 목록) 제거
- `window.renderAnnualList2 = () => renderAnnualMain()` 래퍼로 교체 (기존 참조 호환 유지)

### 상태 표시 로직
```
유효 계약: ✅ YYYY년 MM월 DD일 (초록 #16A34A)
만료 계약: ⚠️ 만료 (빨강 #DC2626)
미작성:    미작성 (회색 #9AAABF)
```

### 이슈 & 해결

| 이슈 | 원인 | 해결 |
|------|------|------|
| 코드 수정 후 GitHub 미반영 | 구버전 베이스 파일을 수정해서 업로드 — 그 사이 변경된 커밋 덮어씌워짐 | GitHub 최신 SHA 재확인 후 최신 파일 새로 다운로드·수정·재업로드 |
| renderAnnualList2 제거 후 닫는 `};` 잔존 | str_replace 범위 지정 미스 | 잉여 `};` 별도 str_replace로 제거 |
