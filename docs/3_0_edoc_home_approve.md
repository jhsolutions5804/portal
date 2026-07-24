# 3.0. 전자결재 — 홈 · 결재함

> Firestore 컬렉션: `edoc_daily`, `edoc_leave`, `edoc_resign`, `edoc_cert`, `edoc_purchase`, `edoc_expense`, `edoc_overtime`, `portal_users`
> 최종 수정: 2026-07-24 (전자결재 홈 하단 패널 전체목록 연결 · r2)
> 최초 작성: 2026-07-01 · 작성: 춘식이(Claude)

---

## 개요

전자결재 앱(`portal/edoc/index.html`)의 홈·결재함, 그리고 전 메뉴 공통 레이아웃·네비게이션 규칙. 포털에 iframe으로 임베드되어 동작한다(`?via=portal`).

---

## 탭 구성 (EDOC_TABS)

| key | 제목 | 진입 함수 |
|-----|------|----------|
| home | 전자결재 홈 | `renderEdocHome()` |
| approve | 결재함 | `renderApproveBox()` |
| daily | 업무일지 | `renderDailyMain()` → `renderDailyList()` |
| leave | 연차신청서 | `renderLeaveMain()` → `renderDocList('leave')` |
| resign | 퇴직원서 | `renderDocMain('resign')` → `renderDocList('resign')` |
| cert | 재직증명서 | `renderDocMain('cert')` |
| purchase | 구매품의서 | `renderDocMain('purchase')` |
| expense | 지출결의서 | `renderDocMain('expense')` |
| overtime | 초과근로 | `renderOvertimeMain()` (→ `3_4_edoc_overtime`) |

---

## 포털 임베드 레이아웃 (N2/N4)

`?via=portal` 접근 시 `<html class="portal-embed">` 적용:
- `.app-header`(파란 헤더), `#tabbar`, `#sb`(사이드바) 모두 `display:none`
- PC(900px+): `.tab-content { max-width:1180px; margin:0 auto }` 중앙 정렬
- 각 메뉴 콘텐츠 상단 툴바에 "🏠 전자결재 홈" 버튼(`edocHomeBtnHtml()`) — 헤더가 숨겨지므로 콘텐츠 내부에 배치

---

## 결재함 (N5)

서브탭 2개로 분리:

| 서브탭 | 내용 | 캐시 변수 |
|--------|------|----------|
| 결재대기 | 내 결재 차례 문서 | `_approvePending` |
| 결재완료 | 처리 끝난 문서 | `_approveDone` |

- 전환: `switchApproveSubTab(sub)`, 데이터 로드: `loadApproveData()`, 렌더: `renderApproveListUI()`
- 완결 판단: `status`가 `approved` / `rejected` / `posted`
- 문서 클릭 → `openDocFromHome(d)` → 상세 진입

---

## 네비게이션 — 뒤로가기 (N8/N9)

전역 변수 `_detailBackFn`으로 "직전 화면 복귀" 1단계 기억:

```
결재함에서 문서 클릭 → openDocFromHome
  → _detailBackFn = () => goTab('approve')
  → 상세화면 진입

상세화면 "‹ 목록" 클릭
  → _detailBackFn 있으면 docDetailBack() 호출 (실행 후 즉시 null 초기화)
  → 없으면 기존 목록(renderDocList/renderLeaveMain)으로
```

- daily는 `DOC_CONFIG` 미정의 → `openDocFromHome`에서 `renderDailyDetail`로 분기 (cfg undefined 방지)
- ※ 향후 멀티스텝 뒤로가기 필요 시 `_navStack` 배열로 확장 가능 (코드 주석 기록)

---

## 업무일지 열람 권한 (N6-1)

데이터 모델: `portal_users/{uid}.dailyViewTargets: [열람허용 대상 uid…]`

> 의미: "이 사람(uid)의 업무일지를 볼 수 있는 대상자 목록"

**열람 필터** (`renderDailyList`):
- 관리자(`_isAdmin`): 전체
- 일반: 본인 글 + (다른 사람의 `dailyViewTargets`에 내 uid가 포함된) 그 사람 글

**권한 관리 화면** (`renderDailyPerms`, 관리자 전용):
- 직원 카드별로 "이 직원의 업무일지를 열람할 수 있는 사람" 칩 토글
- `toggleDailyViewTarget` — 칩 클릭 즉시 Firestore 저장

---

## 목록 레이아웃 (N6-2~6)

- 메뉴 진입 시 바로 조회 테이블(`.ptable`) 표시 (메뉴 선택 화면 없음)
- 우측 상단 툴바(`.sec-toolbar`): 🏠 전자결재 홈 + ✏️ 작성 (+ 관리자는 🔑 권한관리)
- `renderDocList(dtype)` 1개 함수가 leave/resign/cert/purchase/expense 5탭 공용
- 연차는 작성 함수가 `renderLeaveWrite`로 별도 → 작성 버튼만 분기
- 초기 로딩 문구 없음(빈 컨테이너) → 데이터 오면 테이블 또는 "등록된 문서가 없습니다"로 채움

---

## 전자결재 홈 대시보드 (`renderEdocHome`) — r2, 2026-07-24

`renderEdocHome()`이 담당하는 홈 화면 구성 (위→아래):

1. 🌴 내 연차 현황 (부여/사용/잔여)
2. KPI 카드 4개(`#edoc-home-kpi`): 결재 요청 / 수신함 / 내 문서 / 게시 문건 — 각 건수 표시
3. 패널 4개(2x2, `#edoc-home-panels`/`panels2`): 내가 결재해야 할 문서 / 수신함(회람) / 내가 작성한 문서 / 게시된 문건 — 최신 8건 미리보기(`rowHtml`, `.slice(0,8)`)

데이터 소스: `window._edocLists = { approve, inbox, mydocs, posted }` (Firestore `edoc_*` 컬렉션 전수 조회 후 분류, 홈 로드 시 1회 계산)

### 전체 목록 보기 — `edocShowList(kind)`

kind: `'approve' | 'inbox' | 'mydocs' | 'posted'`. `window._edocLists[kind]` **전체**(미리보기 8건 제한 없음)를 모달(`#edoc-list-modal`)로 렌더링. 행 클릭 시 `openDocFromHome(d)`로 상세 이동.

**연결 지점(둘 다 동일 모달 호출):**
- KPI 카드 4개 — 카드 전체 `onclick="edocShowList(kind)"`
- 하단 패널 헤더 4개 — `.panel-head`에 `onclick="edocShowList(kind)"` + "전체보기 ›" 표시 (r2에서 신설)

> **r2 배경**: 이전에는 하단 패널이 미리보기 8건만 보여주고 클릭이 안 돼, 전체 목록을 보려면 상단 KPI 카드를 눌러야 한다는 걸 사용자가 알기 어려웠음(대표님 피드백: "게시된 문건도 저기에 리스트 뜨는 것들만 확인할 수 있잖아"). 패널 헤더도 동일 모달로 연결해 두 경로 모두에서 전체 목록에 접근 가능하도록 수정.
> 새 페이지/게시판을 만들지 않고 기존 모달을 재사용 — 리스크 최소화.
> `window._edocLists`가 비동기 로드 전에 클릭하면 빈 목록으로 뜨는 기존 제약은 KPI 카드와 동일하게 유지됨(변경 없음).
