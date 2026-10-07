# 7.103. 개발로그 — 근로자 연명부 실무자 권한 분리 본섭 반영 (2026-10-07)

- 대표님 지시("검증에 있는 거 모두 본섭으로", 규칙 게시 "끝", 데이터 복사 "진행해")로 테섭의 연명부 실무자 권한 분리를 본섭에 반영. 순서: 규칙 게시(대표님) → 데이터 복사 → 코드 → (원본 정리는 별도 승인).
- 보안규칙: 현재 본섭 규칙에 `isRosterUser`·`master_worker_info`·`master_worker_photos` 실무자 규칙만 얹은 파일(Firestore 333줄)과 Storage `roster_health` 실무자 허용(42줄)을 대표님이 콘솔에서 게시. 게시본이 파일과 일치함을 규칙 API로 확인. 로컬 에뮬레이터: 연명부 35개 + 기존 관리자 전용 묶음 27개 시나리오 통과, 테섭(새 플랫폼) 규칙에서도 동일 결과(새 플랫폼 본섭 이전 때 합칠 수 있음).
- 데이터: 본섭 `master_worker_private` 13문서 중 옮길 항목(16항목)이 있는 3문서를 `master_worker_info`로 복사(`roster_migrate.js copy --apply`, 병합·원본 유지), `verify` 통과. 은행·계좌·일당 등 관리자 항목만 있는 10문서는 그대로. 값은 출력하지 않음. 코드 반영 직전에 복사를 한 번 더 맞춤.
- 코드: `pjt_roster/index.html` 2.7.0(테섭과 같은 변경 31덩어리 — 본섭 Firebase 설정·헤더는 유지, 새 플랫폼 의존 코드는 테섭에도 없음), `m/pjt_roster.html`(info + 관리자만 private), `index.html`·`m/pjt.html`(연명부 메뉴 실무자 노출). 같은 날 올린 연명부 2.6.2 기능(SK·화학물질안전원·수료증 PDF·계정)은 그대로 유지.
- 영향 점검: `master_worker_private`를 읽는 다른 화면(`gihoek`·`team`)은 단가(`dailyRate`·`teamRate`)만 쓰므로 변화 없음.
- 백업 `backup/v_roster_open_20261007/`. 원본 정리(`clean`)는 화면 확인 후 대표님 승인 시에만.
