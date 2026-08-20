# 7.27 — 경량 PJT: 일정등록 폼을 메인 PJT(FAB)와 동일하게 개편 (v3.4.0)

**날짜**: 2026-08-20
**대상**: `pjt_light/index.html`

## 배경
사용자가 메인 PJT(FAB)의 일정등록 화면과 경량 PJT의 일정등록 화면 스크린샷 2장을 첨부하며 "일정 등록할 때도 다른 프로젝트랑 동일하게 해줘"라고 요청. 두 화면을 비교한 결과 카테고리 종류, 시간 입력 방식(텍스트 time input vs 시/분 드롭다운), 할 일 체크박스 유무, 등록자 자동입력 여부 등 다수 차이가 있었음.

## 조사
- `pjt/index.html`의 `US_CATS`/`usAutoDetect`/`openUsForm`/`saveUsSched`/`_usSetTodo` 로직을 원본 확인
- 홈 통합캘린더(`index.html`)의 `HOME_SCHED_CATS`는 여전히 구버전 9종(반입/검수/교육/회의/설치/안전/휴무/연차/행정)을 쓰고 있어서, FAB 개별 모듈과 홈 캘린더 사이에 이미 태그 체계가 갈라져 있었음(기존에 알려지지 않았던 부분). 사용자가 첨부한 스크린샷은 FAB 개별 모듈 쪽(품질/기타 포함 8종)이므로, 이번 요청은 그쪽 기준으로 맞추는 것으로 판단하고 진행

## 구현
- `SCHED_CATS`(선택 가능 카테고리): 9종 → 8종(교육/회의/반입/설치/휴무/안전/품질/기타)
- `SCHED_TAG`(색상 매핑)에는 구 태그(검수/연차)를 계속 남겨둬서, 과거에 그 태그로 저장된 일정도 색상이 깨지지 않고 표시됨 (선택지에서만 제외)
- `schedAutoDetect()`: 일정 내용 입력 시 키워드 기반 카테고리 자동 추정 + 힌트 문구, 카테고리를 직접 탭하면 자동추정 중단(`schedCatTouched`)
- `s-todo-wrap`/`setSchedTodo()`/`toggleSchedTodo()`: 할 일 체크 시 시간 입력 블록에 `.disabled`(투명도+포인터이벤트 차단) 부여, 저장 데이터에 `isTodo:true`, `stime`/`etime`은 빈 문자열로 저장
- 시작/종료 시간: `<input type="time">` → 시(0~24)/분(10분 단위) `<select>` 2개 조합. `schedGetTime()`/`schedParseTime()`으로 조합/역파싱
- 등록자: `openSchedForm()` 진입 시 세션 로그인 계정(`loginUserLabel`, 이름+직급)을 자동 채워넣도록 변경(수정 가능한 일반 입력란은 유지)
- `rangeText()`: `isTodo`이거나 `stime`이 없으면 "(시간 미정)" 표기로 통일

## 검증
- `node --check` 문법 검증
- HTML `onclick`/`onchange` 참조 함수 전수 정의 확인
- jsdom + 모의 Firestore로 실행 검증: 등록자 자동입력, 카테고리 칩 8개 렌더, 시/분 select 옵션 개수(25/6), 자동추정 매칭(설치), 할일 토글 시 time-block 비활성화, 저장 데이터 필드(`isTodo`/`stime`/`etime` 포함) 정상 확인

## 배포
- portal-test 선배포 → 확인 → production 배포 (v3.3.0 → v3.4.0)
- 배포 전 `backup/v3.3.0/pjt_light/index.html`에 이전본 백업
