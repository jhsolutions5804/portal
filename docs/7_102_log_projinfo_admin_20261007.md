# 7.102. 개발로그 — 프로젝트 정보 관리자 전용 묶음(코드) + 경량PJT 3.8.3 (2026-10-07)

- 대표님 지시("검증에 있는 거 모두 본섭으로", "하나씩")로 테섭 20261002a·c / 3.8.3을 본섭에 반영 — **코드 먼저, 규칙은 대표님이 콘솔에서 게시**.
- 코드(20261007a): `pjt/index.html`·`pjt_ph4/index.html`·`pjt_light/index.html` 설정 탭 숨김(`body.is-admin`)과 탭 전환 차단, `pjt_light` 입력 권한(`canWork`·`canWorkAny`·`canCheckStage`·`loadTeamMasters`)과 전체 체크 버튼 대상 한정, `index.html` 종료 PJT 재개 버튼·시작일 입력 관리자 전용.
- 테섭 파일과의 차이: 테섭에는 새 플랫폼용 변경(참여 부서·개인 지정 `app/shared/pjt-participants.js`, 임베드 모드, 업무일지 서버 함수 `edocAct` 연동, `?tab=` 바로가기, 조직 구조 부서 목록)이 같은 파일에 섞여 있어 **옮기지 않았다**. 변경 덩어리를 하나씩 골라 같은 논리만 본섭 파일에 적용.
- 규칙(별도 게시): 현재 본섭 규칙에서 `pjt_registry`·`pjt_settings`는 포괄 규칙으로 승인 계정 전체가 쓸 수 있다 → 코드가 먼저 나가도 정상. 규칙 파일은 `rules_projinfo_admin_prod_20261007.rules`(현재 본섭 규칙에 3건만 최소 변경). 로컬 에뮬레이터 시험 27개 시나리오(일반·관리자·GUEST) 전부 통과, 현재 본섭 규칙에서는 제한 항목 7개가 열려 있음을 확인.
- 쓰기 지점 점검: 본섭 코드에서 `pjt_registry`·`pjt_settings`·`gihoek_projects`를 쓰는 곳을 전수 확인 — 일반 계정이 쓰는 것은 `progress`·`manday`와 하위 컬렉션뿐, 정보 수정·종료·재개·삭제·생성은 관리자 화면에서만 호출됨.
- 백업 `backup/v_projinfo_admin_20261007/`(pjt/pjt_ph4/pjt_light/index.html, index.html).
