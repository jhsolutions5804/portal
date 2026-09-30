# 7.69. 개발로그 — 포털 일정 → Outlook 즉시 반영 배포 완료 + 기존 일정 일괄 반영

> 2026-09-30 · 춘식이(Claude) · 대표님 준비 작업 후 본섭(p4ph2-fab-506a7) 서버 함수 배포

## 준비(대표님이 직접 수행)
- Exchange: 공유 사서함 `PJT 일정`(pjt-calendar@jhsol.kr) 생성, 캘린더 `Default`=Reviewer(전 직원 읽기 전용), 대표님 계정 FullAccess
- Entra 앱 `JH Portal Calendar Sync`(클라이언트 ID e947a534-97d1-41f1-b468-c1606b4b8dce): 애플리케이션 권한 `Calendars.ReadWrite` + 관리자 동의, 클라이언트 암호 발급(만료 24개월 — **2028-09 이전 갱신 필요**)
- Exchange `ApplicationAccessPolicy`(RestrictAccess): 그룹 `PJT-Calendar-Sync`(구성원=PJT 일정 사서함) 범위로 제한 → 직원 개인 사서함 접근 시 403 확인
- Firebase CLI로 함수 배포(런타임 Node.js 24, 지역 asia-northeast3), 비밀키는 Secret Manager `MS_CLIENT_SECRET`

## 배포된 함수
- `syncFabSchedule`(user_schedules/{id}), `syncPjtSchedule`(pjt_registry/{pjtId}/schedules/{id}), `outlookBackfill`(관리자 전용 일괄 반영 HTTP)
- 모든 일정(할 일 제외)이 공용 캘린더 한 곳에 `[현장명] [구분] 제목`으로 들어감. 참석자 개인 캘린더 복사는 옵션(`PERSONAL_COPY`, 기본 꺼짐).

## 트러블슈팅 기록
- `User code failed to load ... Timeout after 10000` → 이 PC에서 첫 로드가 느림 → `FUNCTIONS_DISCOVERY_TIMEOUT=120` 후 배포.
- `Failed to create function ... Eventarc Service Agent permission` → 첫 배포 직후 권한 전파 지연 → 몇 분 뒤 재배포로 해결.
- `AADSTS7000215 Invalid client secret` → Secret Manager에 클라이언트 암호 **값**이 아닌 **비밀 ID**가 들어감 → 값으로 재등록(`secrets:set`) 후 재배포. (프로젝트 파일의 값은 토큰 발급 테스트로 유효 확인)

## 검증(2026-09-30)
- 시험 1건 → Graph 조회: 제목 `[P4 Ph2] PH4 EHU 8EA 시운전 및 클리닝`, 10/1 09:00~10:00 KST, 범주 P4 Ph2, 알림 없음/한가함 표시.
- 접근 제한: 앱 토큰으로 jh.kim@jhsol.kr 사서함 접근 → 403 ErrorAccessDenied.
- **기존 일정 일괄 반영**: 대상 177건(할 일·날짜 없는 항목 제외; 메인 PJT + 경량 PJT 6곳)에 동기화 요청 표식(`outlookSyncRequestedAt`, 일정 내용과 무관)을 넣어 저장 이벤트를 발생시킴 → 공용 캘린더 177건 = 동기화 기록 177건, 현장별: P4 Ph2 151 / H3 17L 16 / P&T3 8 / P3 Ret 1 / M15X 1, 현장명 접두 없는 일정 0, 미해결 오류 0.

## 운영 메모
- 일정은 포털→Outlook 한 방향. Outlook에서 고친 내용은 다음 포털 수정 때 덮어써짐.
- 오류는 Firestore `outlook_sync_errors`에 기록(권한 403 등). 직원 안내: Outlook에서 *캘린더 추가 → 디렉터리에서 → PJT 일정*.
- 권장 후속: `outlook_sync`·`outlook_sync_errors` 관리자 전용 규칙(대표님이 콘솔에서 게시), 클라이언트 암호 만료 알림.
