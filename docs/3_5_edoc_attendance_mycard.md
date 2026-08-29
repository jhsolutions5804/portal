# 3.5. 전자결재 — 출퇴근 기록 · 인사카드

> Firestore 컬렉션: `worker_attendance_log/{workerId}_{date}`, `workers/{workerId}`
> 최초 작성: 2026-08-29 · 작성: 춘식이(Claude)

---

## 출퇴근 기록 (`renderAttendanceTab`)

edoc 내부 네이티브 탭(사이드바·모바일탭바 `goTab('attendance')`)으로 동작 — 별도 페이지 아님. 별도 페이지(`attendance/index.html`)로 처음 만들었다가 포털 프레임 이탈 문제로 edoc 탭으로 흡수 통합함(2026-08-29).

- **오늘 날짜만 기록 가능** (의도된 제약). 과거 날짜 보정은 인사 → 근로시간 탭에서 관리자가 처리 (`2_8_hr_worktime.md` 참고).
- 출퇴근시간 입력은 10분 단위로 자동 스냅(`attSnapTo10Min`, `step="600"` 속성이 일부 브라우저(Android)에서 무시되는 문제 대응 — change 이벤트에서 재보정).
- 근무시간 = (퇴근−출근) − 휴게시간(기본 120분, 수정 가능).
- **월별 근로시간 조회**: 월 이동(◀▶) + 월 라벨 클릭 시 연도이동+12개월 그리드 팝업(`attOpenMonthPicker`)으로 원하는 달로 바로 이동.
- 해당 월 상세 내역 테이블: 휴게시간은 분(分) 단위 입력이지만 표시는 시간(h) 단위로 변환.
- `_myWorkerId` 해석: `portal_users.workerId` 우선, 없으면 `workers.portalUid` 역조회로 보완(근무자 연동 경로가 두 가지라 이중 확인 필요).

## 개인 인사카드 (`renderMyCard`)

로그인 계정과 매칭된 `workers` 문서 1건만 조회 — 이름/직급/소속/사번/입사일/연락처/주소/주민번호(마스킹)/계좌번호(마스킹) 표시. 타인 정보 접근 불가.

---

## 연관 문서
- 근로시간 자동계산 로직: `2_8_hr_worktime.md`
- 유급휴가 캘린더·법정휴가 종류 개편: `3_1_edoc_daily_leave.md` 추가분 참고
