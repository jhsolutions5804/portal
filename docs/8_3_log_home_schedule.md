# 8_3 · 홈 일정 상세/등록/수정/삭제 (r1)

**작업일**: 2026-07-08
**대상**: `index.html` (portal 홈)
**요청**: 홈 우측 상세 일정 클릭 시 세부 내역 확인 + 홈에서 일정 등록·수정 가능하게

## 변경 내용
- 홈 우측 상세 패널(`pjt-cal-detail`)의 각 일정에 **클릭 이벤트** → 상세 모달
- 상세 모달: 카테고리·일정·기간·장소·참석자·등록자·프로젝트 + [수정][삭제][닫기]
- 상세 패널 상단 **＋ 일정 등록** 버튼 → 등록 폼 모달
- 등록 폼: 프로젝트 선택·내용·카테고리(칩)·시작/종료 일시(date+time)·장소·참석자·등록자
- 저장/수정/삭제 후 캘린더·상세 자동 새로고침

## 데이터
- 컬렉션: 선택 PJT에 따라 `user_schedules`(FAB) / `ph4_schedules`(SUP)
- 필드: reg/text/place/att/tag/tagLabel/sdate/edate/stime/etime/isTodo/savedAt — **PJT 앱과 동일** (양방향 호환)
- 신규: addDoc / 수정: setDoc merge(원 컬렉션·id 유지) / 삭제: deleteDoc
- 캐시(`_pjtCalCache`)에 문서 `id`·`col` 추가 (수정/삭제용)

## 신규 함수 (window)
openHomeSchedDetail, closeHomeSchedDetail, openHomeSchedForm, closeHomeSchedForm,
editHomeSchedFromDetail, saveHomeSched, deleteHomeSched, _hscPickCat
(+ 내부: _hscRangeText, _hscRenderCats)

## 배포 전 검토 (본섭 안전성)
- 식별자·element id 중복 없음, let/const 선언 유일 (SyntaxError 위험 없음)
- 의존 심볼 전부 동일 script 블록 → 스코프 정상
- 캐시 id/col 추가는 기존 소비처(tag/stime만 읽음)에 영향 0
- z-index 40(기존 프로필 모달과 동일), 상위 z-index는 모바일 전용(PC display:none)
- 모바일은 m/home.html 리다이렉트 → 새 코드 PC 전용, 무영향

## 검증
- `node --check`: script 블록 2개 정상
- jsdom 흐름(상세→수정→저장→신규→검증차단→삭제): production·test 각 **29/29 통과**
- prod↔test diff: Firebase config·URL·배너 등 레포 고유 차이만

## 배포
- test(portal-test): `5b847db2`
- production(portal): `ae103662`
- backup: **v2.3.0** (index.html)
