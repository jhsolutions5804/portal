# 7.65. 설계·개발로그 — 포털 일정 → Outlook 즉시 반영 (추가 과제 ⑥)

> 2026-09-30 · 춘식이(Claude) · **코드 작성·검증 완료, 배포 전(대표님 준비 작업 대기)**

## 결정
- 즉시 반영 방식: Firestore 트리거 → 서버 함수(Cloud Functions, 서울 `asia-northeast3`) → Microsoft Graph(애플리케이션 권한 `Calendars.ReadWrite`). 포털 화면 코드 변경 없음.
- 대표님 결정(2026-09-30, 개정): **회사 일정이므로 참석자 지정과 무관하게 모든 일정을 공용 PJT 일정 캘린더(공유 사서함) 한 곳에 반영**. (초안은 '참석자 지정 시 개인 캘린더'였으나 폐기) 참석자 개인 캘린더 복사는 옵션 `PERSONAL_COPY`(기본 꺼짐).
- **현장 구분(개정)**: 제목 `[현장명] [구분] 내용` + Outlook 범주(현장명·구분). 현장명은 프로젝트 기본정보의 현장명(경량 PJT=`pjt_registry.site`, 메인 PJT=기획 프로젝트(연동 p4ph2)의 `site`, 비면 PJT 코드). 프로젝트 기본정보 통일은 7_66 참조. Outlook 범주 색은 사용자별 설정이라 자동 색상은 보장하지 않음(제목 접두가 확실한 구분 수단). PJT별 하위 캘린더는 관리 작업이 늘어 다음 단계로 보류.

## 데이터 근거 (본섭, 읽기 전용)
- `user_schedules` 214건: 참석자(`att`)는 자유 입력 문자열이며 212건 중 159건이 빈 값. 시간 없는 일정 73건 → 종일 일정 처리.
- 경량 PJT 6곳은 `pjt_registry/{id}/schedules`에 같은 필드 구조. SUP(`ph4_schedules`)는 종료되어 제외.
- Firestore 위치 `asia-northeast3`, Cloud Functions API는 본섭에서 아직 미사용(제 서비스 계정은 API 활성화·배포 권한 없음 확인) → 배포는 대표님 PC(Firebase CLI).

## 구현
- `outlook-sync/functions/lib/core.js`: 참석자 파싱·대상 결정·이벤트 변환·동기화(생성/수정/삭제/건너뜀).
- `outlook-sync/functions/index.js`: 트리거 2개(`syncFabSchedule`, `syncPjtSchedule`), Graph 호출(토큰 캐시, 429/5xx 재시도), 오류 기록(`outlook_sync_errors`), 매핑 저장(`outlook_sync`), 일괄 반영 함수(`outlookBackfill`, 관리자 전용).
- 규칙: 모든 일정 공용 캘린더 1곳, 할 일 제외, 시간 없음=종일(종료는 다음날 0시), 완료=✔ 접두, 공용 알림 없음(개인 복사 옵션 시 15분 전 알림), Outlook에서 삭제됐으면 재생성.

## 검증
- 단위 테스트 15건(참석자 파싱, 대상 결정, PJT 접두·범주, 종일/시간·자정·월말 경계, 건너뜀, 삭제, 404 재생성, HTML 이스케이프 등) + 트리거 통합 테스트(실제 firebase-functions 라이브러리 + 가짜 Firestore/Graph: 공용 생성·참석자 지정 수정(PATCH)·경량PJT·삭제·403 기록만·500 재시도).
- **실제 Microsoft 365·Firebase 연동은 미검증**(배포 후 확인 필요).

## 대표님 준비 항목
1. 공유 사서함(예: pjt-calendar@jhsol.kr) 생성 + 전 직원 캘린더 조회 권한 (**모든 일정이 여기로 들어가므로 필수**)
2. Entra 앱 권한 `Calendars.ReadWrite`(애플리케이션) + 관리자 동의 + 클라이언트 비밀 발급 + (권장) Exchange에서 접근 범위 제한
3. Firebase CLI로 시크릿 등록·함수 배포 (절차: 전달한 README 참조)
4. (권장) `outlook_sync*` 컬렉션 관리자 전용 규칙 게시

## 후속
- 배포 후 기존 일정 일괄 반영(`outlookBackfill`)을 포털 설정의 관리자 버튼으로 연결.
- 산출물은 GitHub Pages에 올리지 않고 별도 압축 파일(`outlook-sync.zip`)로 전달함.
