# 7.101. 개발로그 — 연명부 2.6.x · 모바일 인사 전체 보기 보완 · 채용 폼 생년월일 검증 (2026-10-07)

- 연명부 2.6.0~2.6.2(`pjt_roster/index.html`, `m/pjt_roster.html`): SK하이닉스 사내화 교육 5종·행복한 만남 계정, 화학물질안전원 교육시스템 슬롯(계정·종사자 교육 연 2시간·수료증 PDF), 목록 칩. 본섭 구조(`master_worker_private`)에 필드만 추가 — 규칙 변경 없음. 상세는 `4_5_pjt_roster.md` 2.6.x 절.
- 모바일 인사(`m/hr.html`, m-hr 20261007a): 주민번호 '전체 보기' 버튼 터치 영역 44px, 화면 이동(`nav`·`popstate`)·`pagehide` 시 즉시 숨김, `aria-pressed`·`aria-label`.
- 홈페이지 채용 폼(`jhsolutions5804.github.io`의 `recruit.html`, build 20261007a): 생년월일 제출 검증(연도 미완성·없는 날짜·범위 밖 차단, 1930~만 15세) — 본섭 포털이 아니라 홈페이지 저장소에 반영(커밋 00f8c2f).
- 테섭에서 먼저 검증(연명부 2.6.2 build 20261007h, m-hr 20261007a, recruit-test 20261002b) 후 대표님 지시("검증에 있는 거 모두 본섭으로")로 본섭 반영. 본섭 구조가 달라 테섭 파일을 복사하지 않고 같은 논리를 본섭 파일에 따로 적용.
- 반영 제외(규칙 게시·서버 배포·데이터 이전 필요 — 별도 순서로 진행): 연명부 실무자 권한 분리(`master_worker_info`)·조회/수정 모드, 프로젝트 정보 관리자 전용 묶음(규칙 3건), 경량PJT 3.8.3, PJT 참여 부서·개인 지정, 새 플랫폼(app)·전자결재 v2.
- 백업 `backup/v_roster_2_6_2_20261007/`(pjt_roster/index.html, m/pjt_roster.html, m/hr.html).
