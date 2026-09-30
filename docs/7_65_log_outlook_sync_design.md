# 7.65. 설계·개발로그 — 포털 일정 → Outlook 즉시 반영 (추가 과제 ⑥)

> 2026-09-30 · 춘식이(Claude) · **코드 작성·검증 완료, 배포 전(대표님 준비 작업 대기)**

## 결정
- 즉시 반영 방식: Firestore 트리거 → 서버 함수(Cloud Functions, 서울 `asia-northeast3`) → Microsoft Graph(애플리케이션 권한 `Calendars.ReadWrite`). 포털 화면 코드 변경 없음.
- 대표님 결정(2026-09-30): **참석자 지정이 없으면 공용 일정으로 보고 공용 PJT 일정 캘린더(공유 사서함)에 반영**, 참석자가 지정되고 포털 계정과 매칭되면 그 사람 개인 캘린더에 반영.

## 데이터 근거 (본섭, 읽기 전용)
- `user_schedules` 214건: 참석자(`att`)는 자유 입력 문자열이며 212건 중 159건이 빈 값. 시간 없는 일정 73건 → 종일 일정 처리.
- 경량 PJT 6곳은 `pjt_registry/{id}/schedules`에 같은 필드 구조. SUP(`ph4_schedules`)는 종료되어 제외.
- Firestore 위치 `asia-northeast3`, Cloud Functions API는 본섭에서 아직 미사용(제 서비스 계정은 API 활성화·배포 권한 없음 확인) → 배포는 대표님 PC(Firebase CLI).

## 구현
- `outlook-sync/functions/lib/core.js`: 참석자 파싱·대상 결정·이벤트 변환·동기화(생성/수정/삭제/건너뜀).
- `outlook-sync/functions/index.js`: 트리거 2개(`syncFabSchedule`, `syncPjtSchedule`), Graph 호출(토큰 캐시, 429/5xx 재시도), 오류 기록(`outlook_sync_errors`), 매핑 저장(`outlook_sync`), 일괄 반영 함수(`outlookBackfill`, 관리자 전용).
- 규칙: 할 일 제외, 시간 없음=종일(종료는 다음날 0시), 완료=✔ 접두, 개인 15분 전 알림·공용 알림 없음, 참석자 변경 시 빠진 사람 일정 삭제, Outlook에서 삭제됐으면 재생성.

## 검증
- 단위 테스트 14건(참석자 파싱, 대상 결정, 종일/시간·자정·월말 경계, 건너뜀, 삭제, 404 재생성, HTML 이스케이프 등) + 트리거 통합 테스트(실제 firebase-functions 라이브러리 + 가짜 Firestore/Graph: 생성·참석자 변경·경량PJT·삭제·403 기록만·500 재시도).
- **실제 Microsoft 365·Firebase 연동은 미검증**(배포 후 확인 필요).

## 대표님 준비 항목
1. 공유 사서함(예: pjt-calendar@jhsol.kr) 생성 + 전 직원 캘린더 조회 권한
2. Entra 앱 권한 `Calendars.ReadWrite`(애플리케이션) + 관리자 동의 + 클라이언트 비밀 발급 + (권장) Exchange에서 접근 범위 제한
3. Firebase CLI로 시크릿 등록·함수 배포 (절차: 전달한 README 참조)
4. (권장) `outlook_sync*` 컬렉션 관리자 전용 규칙 게시

## 후속
- 배포 후 기존 일정 일괄 반영(`outlookBackfill`)을 포털 설정의 관리자 버튼으로 연결.
- 산출물은 GitHub Pages에 올리지 않고 별도 압축 파일(`outlook-sync.zip`)로 전달함.
