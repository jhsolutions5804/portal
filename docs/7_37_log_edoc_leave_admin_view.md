# 연차신청서 — 관리자 전 직원 신청 내역 조회 (2026-09-16)

> 작성: 춘식이(Claude)

## 요청
대표님(스크린샷) — 연차신청서 화면에서 내 계정(관리자)으로 들어가면 모든 직원이 작성한 신청서를 조회할 수 있게 해달라.

## 진단
`fetchEdocDocs('leave')`는 관리자 계정일 경우 이미 `edoc_leave` 컬렉션 전체를 반환하고 있었음(`_isAdmin` 분기, 기존 캘린더 표시용 `_leaveAllDocs`가 이 데이터를 담음). 문제는 화면 쪽 — 우하단 "내 연차 신청 내역" 패널(`leaveRenderMyList`)이 권한과 무관하게 항상 `_leaveMyDocs`(본인 작성분만 필터)만 렌더링하고 있어, 데이터는 이미 있는데 화면에서 막혀 있었음.

## 수정
`edoc/index.html`
- `renderLeaveMain`: 패널 제목을 `_isAdmin ? '전 직원 연차 신청 내역' : '내 연차 신청 내역'`로 분기.
- `leaveRenderMyList`: 목록 소스를 `_isAdmin ? _leaveAllDocs : _leaveMyDocs`로 분기. 관리자 조회 시 각 행 앞에 작성자 이름·직급을 표기해 여러 직원 건을 구분 가능하도록 함.
- 별도 Firestore 쿼리 추가 없음(기존 관리자 전체조회 데이터 재사용) — 성능 영향 없음, 일반 직원 권한 변경 없음.

## 검증
- JS 구문(`node --check`, module 블록 추출 후 import 제거 방식) 통과 — production/portal-test 두 파일 모두.
- CSS 중괄호 depth 검증 통과.
- production ↔ portal-test 두 파일의 Firebase 설정 블록을 제외한 diff가 이번 패치 3곳(패널 제목, srcDocs 분기, 행 렌더링)에만 존재함을 확인 후 각 레포 원본에 동일 패치를 독립 적용.

## 배포
대표님 지시("동시에 해") 따라 production + portal-test `edoc/index.html` 동시 배포. 버전 4.1.1 → 4.2.0.
