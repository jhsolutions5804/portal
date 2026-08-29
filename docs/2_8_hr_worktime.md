# 2.8. 인사 — 근로시간

> Firestore 컬렉션: `worker_attendance_log/{workerId}_{date}` (직원 개인 출퇴근 기록, edoc 출퇴근 기록 탭에서 작성)
> 최초 작성: 2026-08-29 · 작성: 춘식이(Claude)

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
