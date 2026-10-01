# 7.89. 개발로그 — 근로자 명부 보안 강화(민감 정보 분리·임의 ID·기획 관리자 전용·명부 쓰기 잠금) 본섭 반영

> 2026-10-01 · 춘식이(Claude) · 대표님 지시: "기획도 인사랑 똑같아, 관리자 계정들만" / "기획·인사 접근 가능한 계정은 김종화·김민서·김영희·송지훈 4명" / "본섭"

## 발견(문제)
- 인사 화면은 관리자 전용이지만, 데이터는 Firestore에 있고 서버 규칙이 막아야 한다. 일반 직원이 개발자 도구로 직접 요청하면 `workers`(근로자 명부)의 민감 항목(주민번호·계좌·주소·서명)이 읽혔고, 다른 직원의 계좌번호를 바꾸는 것도 가능했다(본섭 규칙 에뮬레이터로 확인).
- 근로자 문서 ID가 '이름_주민번호13자리' 형식이라 필드를 옮겨도 ID로 노출됨. 같은 ID가 근태 기록(`worker_attendance_log`, 일반 직원 열람 가능)·기획 경비(`gihoek_expenses`)·계약서·급여명세서 경로 등에 퍼져 있었음(본섭 1904건 전수 점검).
- 기획(`gihoek_*`) 컬렉션은 승인된 일반 직원이 읽고 수정·삭제할 수 있었음.

## 본섭 반영 (순서)
1. **규칙(v6)** — ruleset 42ef17af…(이전 8343da30…). ① `worker_private`: 관리자 또는 `portalUid` 본인만 읽기·관리자만 쓰기. ② `gihoek_*` 관리자 전용(예외 `gihoek_projects`: 승인된 계정 읽기 + 경량PJT 동기화 6항목 code·name·site·client·contractor·partner 수정만 허용). ③ `workers` 쓰기 관리자 전용(읽기는 승인된 계정 유지, 하위 문서는 관리자만). 백업 `backup/rules/20261001_{before,after}_worker_security.rules`.
2. **민감 항목 복사** — `scripts/worker_private_tools.py copy`: workers 10명 → worker_private 10건(원본 유지, 값 일치 확인).
3. **근로자 문서 ID 이전** — `scripts/migrate_worker_ids.py --env prod --apply`: 근로자 9명의 옛 ID를 임의 ID(`w_`+16자리)로. 경로·필드 값에 옛 ID가 든 문서 새로 만들어 값 검증 255건(실패 0) 후 옛 문서 226건 삭제, 옛 ID 잔존 0건. 대상 컬렉션: worker_attendance_log·payslips·labor_contracts·annual_contracts·workers·worker_private·gihoek_expenses·severance(문서 이동), overtime·edoc_overtime·sign_links·doc_send_log·portal_users·salary_offers(필드 값). 옛→새 매핑은 `portal_secrets/worker_id_migration`(관리자 전용).
4. **코드** — hr 2.25.1(읽을 때 workers+worker_private 합침·저장 시 분리, 등록 시 임의 ID, 같은 이름·주민번호 중복 등록 차단), 모바일 인사(`m/hr.html`), 전자결재 내 정보 PC·모바일, 포털 홈(신규 근로자 문서에 민감 항목 빈 값을 넣지 않음). 백업 `backup/v2.25.1/hr/`.
5. **workers 민감 항목 원본 삭제(완료)** — 대표님이 본섭에서 인사·기획·일반 직원 화면 확인 후("문제 없는 것 같네") `worker_private_tools.py scrub --env prod --apply` 실행: 삭제 전 worker_private 와 값 불일치 0건 확인, workers 10명에서 민감 항목 삭제, 이후 점검 — workers 에 민감 항목 남은 문서 0건, 일반 직원 토큰으로 직접 읽은 근로자 명부 응답에 민감 항목 0개, 본인 worker_private 200, 관리자 worker_private 목록 200(10건). 값은 worker_private 에만 존재.

## 검증
- 에뮬레이터: 기획 209건·worker_private 17건·workers 쓰기 18건·인사 캘린더 62건·채용 26건 통과, 변경 전/후 차분에서 의도한 컬렉션(worker_private·gihoek_*·workers 쓰기) 외 판정 변화 0·관리자 판정 변화 0.
- 본섭 실서버(실제 로그인 토큰, 값은 출력 안 함): 일반 직원 — 기획 견적·경비·정산 403, `gihoek_projects` 200, 본인 worker_private 200·타인 403·목록 403, workers 직급 수정 403. 관리자 — 기획·worker_private·근로계약서 200. 이전 직후 전체 재점검 1922건 중 옛 ID 문서 0건, portal_users 연결·문서 id 필드 정상.
- 규칙 생성 스크립트가 `master_worker_private` 때문에 `worker_private` 규칙을 이미 있다고 오판해 본섭용에서 누락하던 것을 회귀 시험으로 잡아 수정.

## 롤백
- 규칙: `before_worker_security.rules` 재게시. ID: `migrate_worker_ids.py --env prod --rollback`(매핑 문서 사용). 코드: 직전 커밋(28d5e53). scrub(원본 삭제)까지 끝난 뒤에는 코드·규칙만 되돌리면 민감 항목이 안 보이므로, 롤백이 필요하면 worker_private 값을 workers 로 복사하는 작업이 함께 필요하다.

## 알려진 사항·후속
- 본섭 `worker_attendance_log` 는 일반 직원이 서로의 근태 기록을 읽고 쓸 수 있음(ID 노출은 해소됨). 본인 기록만 접근하게 하는 규칙은 별도 과제.
- 이전 매핑 문서는 롤백이 필요 없어지면 삭제.
- 본섭 `test` 계정은 비관리자인데 인사 권한만 켜져 있음(인사 모듈은 관리자만 진입 — 접근은 막혀 있음).
