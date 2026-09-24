# 2.8. 인사 — 근로시간

> Firestore 컬렉션: `worker_attendance_log/{workerId}_{date}` (직원 개인 출퇴근 기록, edoc 출퇴근 기록 탭에서 작성)
> 최초 작성: 2026-08-29 · 최종 수정: 2026-09-23(v2.7.0, 관리자 휴가 직접 부여 추가) · 최종 개정: 2026-09-24(출장 체크 + 여비교통비 연동) · 작성: 춘식이(Claude)

---

## 개요

기존 "초과근로" 메뉴(수당 신청/승인 기반)를 "근로시간"으로 확장 개편. 직원이 edoc 출퇴근 기록 탭에서 매일 본인 출퇴근시간을 입력하면(당일만 가능), 인사에서 그 데이터를 월별로 집계·시각화하고 관리자가 직접 수정할 수 있다. 기존 초과근로 결재(수당 신청) 시스템은 완전히 별개로 그대로 유지된다.

## 자동 계산 값

- **월 소정근로시간**: 해당 월 평일수(공휴일 `KR_HOLIDAYS` 제외) × 8h. 매달 값이 다름(예: 2026-07=184h, 2026-08=160h).
- **월 최대초과근로시간**: 근로기준법 연장근로 한도(주 12h) × 해당월과 겹치는 ISO주수.
- **유급휴가 반영**: 승인/게시된 유급 연차만 근무시간에 합산 (1일=8h, 반차=4h). `computeLeaveHoursForMonth`/`hrComputeLeaveHoursForMonth`.

⚠️ **타임존 버그(2026-08-29 수정)**: 날짜 문자열을 `date.toISOString().slice(0,10)`으로 만들면 KST(+9) 브라우저에서 하루 밀린다(UTC 변환 때문). 반드시 `date.getFullYear()+'-'+...+'-'+...` 형태로 로컬 날짜를 직접 조합해야 함. hr/edoc/attendance 3개 파일의 `monthlyStandardHours` 계열 함수 전부 이 방식으로 수정됨.

## 인사 → 근로시간 탭 (관리자 전용, `otPcShowPersonDetail`)

- 직원 선택 시 `otGetAttendanceSummary(workerId, year, month, workerName)`로 소정/최대초과/누계/유급휴가 반영시간 카드 표시 (`otRenderAttendanceCard`).
- **근로 내역 캘린더** (`otRenderAttendanceCalendar`): 표 대신 달력으로 표시. 날짜 클릭 시 추가/수정 팝업(`otAttOpenEdit`).
  - 🔵 파랑: 정상 근무 / 🟡 노랑: 연차·휴가(승인된 것만, `leaveOnDate`로 결근과 구분) / 🔴 빨강: 평일 결근(기록·연차 둘 다 없음) / 🟣 보라: 휴일근무 / 주황 점: 관리자 수정 표시(`updatedByAdmin:true`)
- 팝업 내 "📋 업무일지" 버튼 → `otShowDailyReport(workerName, date)` — `edoc_daily`를 `authorName`+`date`로 조회해 그 날짜 업무일지 표시.
- 좌측 하단 옛 "➕ 초과근로 입력" 폼(overtime 컬렉션 수동입력)은 제거됨. 초과근로수당(급여 연동)은 이제 실근무기록 기반으로 급여명세서 작성 시 자동 계산되므로 불필요.

## 관리자 휴가 직접 부여 (v2.7.0, 2026-09-23)

**요청**: 대표님 — 근로시간 탭에서 연차·근무시간을 관리자가 직접 넣을 수 있게 해달라. (근무시간 직접 입력은 위 `otAttOpenEdit`으로 기존에 있었음 — 이번 건은 휴가 쪽 보완이며, 헷갈리지 않도록 "➕ 기록 추가" 버튼명도 "➕ 근무시간 추가"로 바꿈.)

기존에는 관리자가 연차를 직접 등록하려면 "연차 현황" 탭으로 이동해 `openLeaveAdminForm()`을 열어야 했다. 근로시간 탭에서 근무 내역을 보다가 바로 휴가를 넣거나 고칠 수 있도록 진입 경로를 추가했다(신규 로직 없이 기존 `edoc_leave` 등록 폼을 재사용).

- **`otPcShowPersonDetail` 헤더**: "🌴 휴가 부여" 버튼 추가 → 오늘 날짜로 `openLeaveAdminForm(null, preset)` 호출.
- **`otAttOpenEdit`(날짜 클릭 모달)**: 상단에 그 날짜의 휴가 상태를 보여주는 배너 삽입.
  - 이미 승인/게시된 연차 기간에 포함된 날짜 → `🌴 OO 기간입니다 (시작~종료)` + `수정/삭제` 버튼(해당 `edoc_leave` 문서 id로 편집 모드 오픈).
  - 휴가가 없는 날짜 → `🌴 이 날짜에 휴가 부여` 버튼(그 날짜를 시작·종료일로 프리필한 신규 등록 모드 오픈).
  - 날짜별 조회를 위해 `otPcShowPersonDetail`이 로드한 해당 근로자의 연차 목록을 `_otLeaveCache[workerName]`(id 포함)에 캐시해 둔다.
- **`openLeaveAdminForm(editId, preset)`**: `preset`(근로자명·날짜·복귀정보) 파라미터 추가. `preset.workerName`으로 근로자 선택 드롭다운을 프리필하고, `preset.date`를 시작일·종료일 기본값으로 채운다. 기존 "연차 현황" 탭에서의 무인자 호출은 그대로 동작(하위호환).
- **복귀 처리**: 모달에 `dataset.returnJson`으로 "어디서 열렸는지"(`{type:'ot', workerId, workerName, rank}`)를 심어두고, 저장/삭제 후 `leaveAdminReturn()`이 이를 읽어 근로시간 탭에서 열렸으면 `otPcShowPersonDetail`로, 아니면 기존처럼 `renderLeaveStatusMain()`으로 되돌아간다.
- 저장되는 데이터는 기존 "연차 현황"의 관리자 등록과 완전히 동일(`edoc_leave`, `adminCreated:true`, `status:'posted'`) — 별도 컬렉션·필드 추가 없음.

## 출장(여비교통비 연동) 체크 (2026-09-24, hr v2.1x)

**요청 배경**: 급여명세서 여비교통비 항목을 매번 수기로 입력하지 않고, 근로시간 탭에서 이미 관리하는 출퇴근 기록에 "이 날은 출장"만 체크해두면 급여명세서 작성 시 자동으로 불러오도록 함.

- **`otAttOpenEdit`(날짜 클릭 모달)**에 "✈️ 출장" 체크박스 추가(`#ot-att-trip`, `otAttTripToggle(this)`). 체크하면 출장 유형 선택 드롭다운이 나타남(`PS_TRAVEL_TYPE_LABEL` — 급여명세서 여비교통비 유형과 동일한 목록, `#ot-att-triptype`).
- **저장**(`otAttSave`): `worker_attendance_log` 레코드에 `isBusinessTrip`(bool)·`tripType`(문자열) 필드로 함께 저장. 체크 해제 시 `tripType`은 빈 문자열.
- **캘린더 표시**(`otRenderAttendanceCalendar`): 출장일은 ✈️ 아이콘 표시, 상세 카드 헤더에 "이번달 출장 N일" 요약.
- **급여명세서 연동**: `psFetchAttendanceData`가 해당 월 출퇴근 기록을 모을 때 `isBusinessTrip:true`인 날짜들을 `businessTrips: [{date, tripType}]` 배열로 함께 반환(`ps.attBusinessTrips`에 캐시). 급여명세서 여비교통비 입력란의 "📥 근로시간에서 불러오기" 버튼(`psImportTravelFromAttendance`)을 누르면 `tripType`별로 일수를 집계해 여비교통비 항목에 자동 반영 — 상세는 `2_5_hr_payslip_r3.md` 참고.

## 관련 함수 위치 (hr/index.html)

- `monthlyStandardHours`, `monthlyMaxOvertimeHours`, `_isoWeekKey`: 캘린더 기준 시간 계산
- `hrComputeLeaveHoursForMonth`: 유급휴가 → 근무시간 환산
- `hrCalcNightHours`: 22:00~06:00 야간시간 계산 (급여명세서용)
- `hrCalcWeeklyHolidayPay`: 주휴수당 개근판정 (급여명세서용, 2_5 문서 참고)
- `hrCalcHolidayPay`: 휴일근로수당 계산 (급여명세서용)
- `otGetAttendanceSummary`, `otRenderAttendanceCard`: 요약 카드
- `otRenderAttendanceCalendar`, `otAttOpenEdit`, `otAttSave`, `otAttDelete`: 근로 내역 캘린더 CRUD
- `otShowDailyReport`: 업무일지 팝업

## edoc 쪽 (직원 셀프서비스, edoc/index.html)

- `renderAttendanceTab`(출퇴근 기록 탭, 전자결재 내부 네이티브 탭 — 별도 페이지 아님, `goTab('attendance')`)
- 오늘 날짜만 입력 가능(의도된 제약, 과거 날짜 보정은 인사 관리자가 근로시간 탭에서 처리)
- 시간 입력은 10분 단위로 자동 스냅(`attSnapTo10Min`) — 일부 브라우저(Android)가 `step="600"` 속성을 무시하는 문제 대응
- 월 이동(◀▶) 및 월 선택 팝업(연도 이동 + 12개월 그리드, `attOpenMonthPicker`)
- 해당 월 상세 내역 테이블(휴게시간은 분→시간(h) 단위로 표시)
