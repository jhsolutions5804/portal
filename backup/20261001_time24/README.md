# 시간 입력 24시간 통일 (2026-10-01, 본섭)
- 공용 `time24.js` — 모든 `<input type="time">`을 24시간(HH:MM) 입력 칸으로 자동 변환(동적 생성 칸 포함).
- 적용 화면(7): index.html, hr/index.html, edoc/index.html, daily-report/index.html, m/edoc.html, m/pjt.html, m/schedule.html (`<head>` 첫머리에 스크립트 태그). 출퇴근 기록(attendance)은 본섭에 없는 모듈이라 테섭에만 적용.
- hr 2.27.0: 채용 지원자 면접 일시를 datetime-local → 날짜 + 24시간 시간 두 칸(`applicantsIvChange`).
- 되돌리기: 각 파일의 time24.js 스크립트 태그 한 줄 제거(또는 커밋 f369bc5 revert).
