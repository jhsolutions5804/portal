# 3.0. 전자결재 — 홈 · 결재함

> Firestore 컬렉션: `edoc_daily`, `edoc_leave`, `edoc_resign`, `edoc_cert`, `edoc_purchase`, `edoc_expense`, `edoc_overtime`, `portal_users`
> 최종 수정: 2026-07-27 (via=portal 우회 버그 수정 · r4) · 최초 작성: 2026-07-01 · 작성: 춘식이(Claude)

---

## 접근 검증 (2026-07-27)

- `onAuthStateChanged` 콜백에서 항상 `portal_users/{uid}` 문서를 조회해 `status==='approved' && (admin || perms.edoc)`을 확인한 뒤에만 `enterApp()` 진입 — via=portal 여부와 무관하게 동일 기준 적용
- ⚠️ 과거엔 `?via=portal` 파라미터가 있으면 승인·권한 여부와 무관하게 무조건 입장시키는 우회 버그가 있었음(주소창에 `?via=portal`만 붙이면 미승인 계정도 진입 가능). 이번 수정으로 두 경로 모두 동일한 검증을 거치도록 통합함
- via=portal일 때는 검증 통과 후 `document.documentElement.classList.add('portal-embed')`만 추가로 적용(포털 임베드 스타일용), 직접 접근 시엔 미적용 — 이 차이만 유지하고 나머지 검증 로직은 완전히 동일


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

### 🐛 미해결 — 결재함에 초과근로 누락 (2026-07-23 발견)

`loadApproveData()`가 조회하는 `DOC_TYPES` 배열에 `'overtime'`이 빠져있음. `TYPE_LABEL`에는 `overtime:'초과근로'`가 이미 등록돼 있어 원래 의도는 결재함 노출이었던 것으로 보이나, 실제로는 `edoc_overtime` 컬렉션을 아예 조회하지 않아 결재함에 절대 나타나지 않는다. 현재는 "전자결재 → 초과근로" 전용 탭(`renderOvertimeMain`)에서만 승인 가능. `DOC_TYPES`에 `'overtime'` 추가 여부는 다음 세션 과제로 남김.

---

## 승인 처리 — `docApprove()` (범용, 모든 dtype 공통)

문서 상세(`docDetail`)의 승인/반려 버튼에서 호출. **승인 버튼이 보이는 조건과, 실제 결재라인을 갱신하는 조건이 서로 다른 로직으로 구현되어 있었다가 2026-07-26에 통일함.**

- 버튼 노출(`docDetail`의 `canApprove`): `isMyTurn`(결재라인에 내 uid/이름이 있고 내 차례) **OR** `_isAdmin && (status pending/reviewing)` — 관리자는 결재라인에 없어도 버튼이 보임
- 실제 처리(`docApprove`의 대상 단계 결정): 2026-07-26 이전에는 uid/이름 일치만 확인하고 **관리자 예외가 없어서**, 관리자가 대신 승인하면 결재라인이 하나도 갱신 안 된 채 저장을 시도하다 실패 → 문서가 계속 `pending`으로 남는 버그가 있었음(`3_4_edoc_overtime` r5 참조, 실제 발생 사례로 발견·수정)
- **수정 후**: `docApprove()`도 순번 기반으로 "이전 단계가 모두 끝난, 차례가 된 단 하나의 단계"를 먼저 uid/이름으로 찾고, 없으면 관리자가 그 단계를 대신 처리하도록 통일. 다단계 결재라인(결재1→결재2 등)에서 관리자가 눌러도 한 단계씩만 처리되도록 `targetIdx`를 하나로 고정해 다단계 동시승인 사고를 방지함.
- 최종 결재자 판단(`isLastApprover`), 게시 가능 여부(`canPost`), 회수(`canRecall`), 수정(`canEdit`) 등 나머지 권한 로직은 `docDetail()`에 그대로 있음 — 상세는 코드 참조.

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

