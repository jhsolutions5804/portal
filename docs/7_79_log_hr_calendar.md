# 7.79. 개발로그 — 인사 캘린더 신설 및 본섭 반영 (hr 2.19.0~2.23.0)

> 2026-10-01 · 춘식이(Claude) · 대표님 지시: "본섭에 반영하면서 hr calendar 사서함도 outlook 배포하자"

## 경과
- 대표님이 Exchange 공유 사서함 `인사 일정`(hr-calendar@jhsol.kr)을 생성. 폴더 권한: Default·Anonymous=None, 김종화·김민서·김영희·송지훈=Editor (PowerShell 결과 확인).
- 테섭에서 2.19.0(신설)→2.20.0(홈 2단)→2.21.0(날짜 선택·공휴일)→2.22.0(연차)→2.23.0(면접·제안서 자동 등록) 순으로 구현·검증 후 본섭 반영.
- 대표님 결정: 일정 구분 5종(면접·연봉제안서 회신·연봉협상·인사평가·기타), 접근 4명 한정, 날짜 클릭은 선택만, 연차 표시, Outlook 반영은 면접·제안서 자동 등록까지 만든 뒤 한 번에.

## 본섭 반영 내역 (2026-10-01)
1. **Firestore 규칙**: 백업 `backup/rules/20261001_before_hrcal.rules` → 게시(ruleset 4910b897…, 이전 6fe5d12a…). `hr_calendar_access`·`hr_calendar_events` 신설 규칙과 관리자 전용 컬렉션 목록 확장만 추가(기존 줄 삭제 1줄: 목록 확장). 게시 직전 현재 규칙이 검증한 버전(6fe5d12a)과 같은지 확인 후 게시.
2. **설정 데이터**: 본섭 `hr_calendar_access/config.emails` = 4명 생성(기존 문서 없음 확인 후).
3. **화면 코드**: hr 2.23.0 + 포털 index.html(인사 하위 탭 `hrcal` 키). 테섭 변경분(082cb68→HEAD)을 패치로 적용 — 파일 통째 복사 금지 원칙 준수. 본섭 고유값(Firebase 설정·EmailJS 키·`_SIGN_BASE`) 유지 검증, 테섭 설정 혼입 없음 검증.
4. 백업: `backup/v2.23.0/hr/index.html`.

## 롤백
- 규칙: 백업 파일을 다시 게시(또는 이전 ruleset 6fe5d12a… 으로 release 변경).
- 화면: 직전 커밋으로 되돌림(hr 2.18.0).

## 알려진 사항
- 다른 모듈(PJT·경량PJT·전자결재·인사 근로시간)의 공휴일 데이터에 오류·누락이 있음(2026 노동절·부처님오신날, 2027 설날 날짜, 2027 각종 대체공휴일). 별도 정비 대상.
- 근로자 명부·계약서·급여명세서 컬렉션은 규칙상 별도 보호 없이 포괄 규칙(승인 계정 전체)에 해당 — 별도 보강 제안 중.

## Outlook 반영 완료 (2026-10-01, 한국 시간 오후)
- Exchange: `PJT-Calendar-Sync` 그룹에 hr-calendar@jhsol.kr 추가 → `Test-ApplicationAccessPolicy` 허용됨. Graph 접근은 정책 반영 지연으로 약 2시간 뒤 403→200.
- 서버 함수: `outlook-sync:syncHrCalendar`(asia-northeast3, Node 24, 2nd gen) 배포. 소스 `outlook-sync/functions/hr-sync.js` + `index.js` 마지막 줄 export. 대표님 PC `C:\Users\종화\outlook-sync`.
  - 배포 명령(codebase 이름 필요): `firebase deploy --only functions:outlook-sync:syncHrCalendar --project p4ph2-fab-506a7`
- 실서버 시험(임시 일정 `hr_calendar_events/zz_outlook_e2e`): 생성 → Outlook 이벤트 `[면접] [시험] …` 10:00~11:00(범주 면접, 바쁨 표시 없음) / 수정(제목·시간) → 같은 이벤트 갱신(중복 없음) / 삭제 → Outlook 이벤트·매핑 문서 삭제. `outlook_sync_errors` 인사 캘린더 오류 0건. 시험 데이터 전부 정리.
- 한계: 포털 → Outlook 한 방향. Outlook에서 고친 내용은 다음 포털 수정 때 덮어쓴다. 접근 전에 만든 일정은 소급 반영되지 않는다(본섭 인사 일정 0건이어서 해당 없음).
