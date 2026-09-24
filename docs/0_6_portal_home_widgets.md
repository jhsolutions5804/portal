# 0.6. 포털 홈 — 출퇴근·업무일지·전체 PJT 일정 위젯 (Outlook 카드 대체)

> 대상: `index.html` (포털 셸 — 포털 홈 대시보드 영역)
> 최초 작성: 2026-09-24 · 작성: 춘식이(Claude)

---

## 요청

대표님 — 포털 홈의 Outlook 메일 카드를 지우고, 그 자리에 출근시간·퇴근시간·업무일지를 놓으면 어떨까. 이어서 홈 하단에 전체 PJT 일정을 볼 수 있는 캘린더도 넣어달라. 프로젝트에 속하지 않는 회사 공통 일정도 등록할 수 있게 해달라.

## 1. Outlook 카드 제거

기존 `renderOutlookCard`(OAuth2 PKCE로 Microsoft 계정 연결 → 읽지 않은 메일 표시) 전체와 관련 헬퍼(`oa2Login`/`oa2Logout`/`clearMsalCache`/`_oa2PKCE`/`OA2` 설정)를 제거했다. `outlook-auth.html`(OAuth 리다이렉트 수신 페이지) 파일 자체는 건드리지 않았으나 더 이상 어디서도 참조되지 않는다.

## 2. 출퇴근 기록 위젯 (`attend-card-wrap`)

- 전자결재 앱의 기존 출퇴근 기록(`worker_attendance_log/{workerId}_{yyyy-mm-dd}`)과 **동일한 컬렉션을 공유** — 홈에서 저장해도, 전자결재에서 저장해도 같은 기록.
- `me.workerId`(포털 로그인 계정 ↔ 근로자 연동 시 `portal_users` 문서에 기록되는 필드)로 대상 근로자를 식별. 연동 안 돼 있으면 "근무자 명부와 연동되어 있지 않습니다" 안내만 표시.
- 출근시간·퇴근시간 두 필드만 노출(휴게시간은 기존 값을 유지하거나 기본 120분). 저장 시 `jhCalcWorkHours()`로 근무시간을 계산해 함께 기록.
- 관련 함수: `renderAttendHomeCard()`, `jhAttendSave()`, `jhTodayKey()`, `jhCalcWorkHours()`.

## 3. 업무일지 위젯 (`daily-card-wrap`)

- `edoc_daily` 컬렉션에서 `authorUid == me.uid`인 문서를 전부 가져와 클라이언트에서 날짜순 정렬(복합 인덱스 요구를 피하기 위해 `orderBy`를 쓰지 않고 단일 `where`만 사용).
- 오늘 작성 여부(문서 중 `date === 오늘`이 있는지) + 최근 5건 목록을 표시. 목록 클릭 또는 "업무일지 바로가기" 버튼은 전자결재 > 업무일지 탭을 연다(`window._goEdocDaily()` → `openModule(MODULES.find(x=>x.key==='edoc'), 'daily')`).
- 읽기 전용 — 작성은 기존 전자결재 업무일지 화면에서.
- 관련 함수: `renderDailyHomeCard()`.

## 4. 홈 대시보드 레이아웃

- `.home-dash` 데스크톱 그리드를 2열→3열로 변경(결재현황 | 출퇴근 | 업무일지).
- 세 카드(`.section-card`, `.outlook-card`) 모두 `min-height:300px`로 높이를 고정해, 목록 길이에 따라 레이아웃이 들쭉날쭉하지 않도록 했다. 목록이 길어지는 결재현황(`.approve-list`, max-height 220px)·업무일지(`.outlook-mail-list`, max-height 150px)는 카드 안에서 스크롤.

## 5. 전체 PJT 일정 캘린더 (홈 하단, 읽기 전용 + 등록)

PJT 관리 화면(PJT 홈)에 이미 있던 캘린더(`0_5`가 아니라 별도 구현 — `renderPjtCal`/`loadPjtCalendar` 등, PJT 홈 자체 상태)와 **데이터 소스는 같지만 완전히 독립된 상태·DOM**으로 새로 만들었다. 기존 PJT 캘린더 코드는 전혀 건드리지 않았다(재사용 시도 시 두 화면이 동시에 열릴 수 있어 상태 충돌 위험이 있다고 판단).

- 상태: `_homeCalY`/`_homeCalM`(연·월)/`_homeCalCache`(월별 일정 캐시)/`_homeCalSel`(선택된 날짜).
- 데이터: `allSchedPjtKeys()`(활성 PJT + 회사 일정 키 전체) 순회하며 `schedColPath(key)` 경로에서 해당 월 범위(`sdate` 필드 기준) 일정을 가져와 날짜별로 합산. FAB(`user_schedules`)·SUP(`ph4_schedules`)·경량PJT(`pjt_registry/{id}/schedules`)·회사 일정(`company_schedules`) 전부 포함.
- 렌더: `renderHomeCal()`(월 그리드, 날짜별 프로젝트 색상 점 `pjtColorFor()`) / `renderHomeCalLegend()`(그 달에 등장한 프로젝트만 범례 표시).
- 날짜 클릭(`homeCalSelectDay(dk)`): 그 날 일정을 프로젝트별 색상 왼쪽 테두리로 요약. **"＋ 일정 등록" 버튼으로 바로 등록 가능**(아래 6번) — 수정·삭제는 "PJT 관리에서 일정 수정·삭제 →" 버튼으로 PJT 홈으로 이동해서 처리(그쪽엔 이미 수정/삭제 UI가 있어 중복 구현하지 않음).
- 저장/삭제(`saveHomeSched`/`deleteHomeSched`, PJT 홈 쪽 공용 함수)가 실행되면 PJT 홈 캘린더뿐 아니라 **홈 캘린더도 함께 새로고침**하도록 양쪽 다 갱신하는 코드를 추가했다.

## 6. 프로젝트에 속하지 않는 "회사 일정"

- 일정 등록 폼(`openHomeSchedForm`)의 프로젝트 선택 드롭다운은 `allSchedPjtKeys()`를 그대로 쓰므로, 이 목록에 회사 일정을 추가하면 폼 수정 없이 자동으로 선택지에 나타난다.
- 구현: `PJT_SCHED_COL`에 `company:['company_schedules']` 추가, `PJT_SUBTABS`에 `{key:'company', name:'회사 일정', emoji:'🏢', url:''}` 추가(이름 조회용).
- `PJT_SUBTABS`는 PJT 사이드바 서브메뉴 목록 생성에도 쓰이므로, `company`가 실제 프로젝트 워크스페이스가 아니라 사이드바에 잘못 노출되지 않도록 아래 3곳에 `.filter(st=>st.key!=='company')`를 추가했다: 데스크톱 사이드바, 모바일/보조 사이드바 렌더, PJT 홈의 프로젝트 카드 목록. 고정 PJT 이름 동기화 루프(`pjt_settings` 조회)에도 `company`는 건너뛰도록 추가.

## 알려진 제약

- 홈 캘린더 상세 패널은 **읽기 전용 요약 + 신규 등록**만 지원. 기존 일정 수정·삭제는 PJT 홈으로 이동해야 한다(중복 UI 방지를 위한 의도적 설계).
- `edoc_daily` 조회 시 인덱스 회피를 위해 정렬을 클라이언트에서 처리 — 사용자 한 명의 업무일지 수가 아주 많아지면(수백 건 이상) 매 홈 진입마다 전체를 읽어오는 비용이 커질 수 있다. 현재 규모에선 문제 없음.
