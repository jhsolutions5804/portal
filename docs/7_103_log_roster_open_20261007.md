# 7.103. 개발로그 — 근로자 연명부 실무자 권한 분리 본섭 반영 (2026-10-07)

- 대표님 지시("검증에 있는 거 모두 본섭으로", 규칙 게시 "끝", 데이터 복사 "진행해")로 테섭의 연명부 실무자 권한 분리를 본섭에 반영. 순서: 규칙 게시(대표님) → 데이터 복사 → 코드 → (원본 정리는 별도 승인).
- 보안규칙: 현재 본섭 규칙에 `isRosterUser`·`master_worker_info`·`master_worker_photos` 실무자 규칙만 얹은 파일(Firestore 333줄)과 Storage `roster_health` 실무자 허용(42줄)을 대표님이 콘솔에서 게시. 게시본이 파일과 일치함을 규칙 API로 확인. 로컬 에뮬레이터: 연명부 35개 + 기존 관리자 전용 묶음 27개 시나리오 통과, 테섭(새 플랫폼) 규칙에서도 동일 결과(새 플랫폼 본섭 이전 때 합칠 수 있음).
- 데이터: 본섭 `master_worker_private` 13문서 중 옮길 항목(16항목)이 있는 3문서를 `master_worker_info`로 복사(`roster_migrate.js copy --apply`, 병합·원본 유지), `verify` 통과. 은행·계좌·일당 등 관리자 항목만 있는 10문서는 그대로. 값은 출력하지 않음. 코드 반영 직전에 복사를 한 번 더 맞춤.
- 코드: `pjt_roster/index.html` 2.7.0(테섭과 같은 변경 31덩어리 — 본섭 Firebase 설정·헤더는 유지, 새 플랫폼 의존 코드는 테섭에도 없음), `m/pjt_roster.html`(info + 관리자만 private), `index.html`·`m/pjt.html`(연명부 메뉴 실무자 노출). 같은 날 올린 연명부 2.6.2 기능(SK·화학물질안전원·수료증 PDF·계정)은 그대로 유지.
- 영향 점검: `master_worker_private`를 읽는 다른 화면(`gihoek`·`team`)은 단가(`dailyRate`·`teamRate`)만 쓰므로 변화 없음.
- 백업 `backup/v_roster_open_20261007/`. 원본 정리(`clean`)는 화면 확인 후 대표님 승인 시에만.

## 원본 정리(clean) — 2026-10-07 (대표님 "원본 정리 진행해. 혹시 롤백 해야할 수 있으니 지금 그대로 백업해두고")
- **정리 전 백업**: `master_worker_private` 13문서·`master_worker_info` 3문서를 관리자 전용 컬렉션 `portal_secrets`에 `roster_backup_20261007__{private|info}__{문서ID}`로 그대로 복사(+ 목록 `roster_backup_20261007__INDEX`), 원본과 Timestamp까지 완전히 같음을 읽어서 확인(`scripts/roster_backup.js`).
- **정리**: 옮긴 항목(16항목×3문서=48개)을 `master_worker_private`에서 삭제 — 은행·계좌·일당·팀 단가는 남김(`scripts/roster_clean_safe.js`). 복사 이후 새 화면에서 저장해 info 쪽이 더 최신이고 값이 다른 항목이 있었으므로(추가분뿐) 기존 `roster_migrate.js clean`의 "값 동일" 조건 대신 "백업과 현재 private 동일 + 지울 항목이 info에 이미 있음" 조건으로 실행. 정리 후 `plan`: 옮길 항목이 있는 문서 0, info는 백업과 동일.
- **롤백**: `scripts/roster_rollback.js`(기본 모의 실행, `--apply`로 private를 백업본으로 덮어씀, `--with-info`는 info도 백업 시점으로 되돌림 — 그 뒤 새로 저장한 내용은 사라짐). 백업 문서는 개인정보 포함 — 문제가 없다고 확인되면 `portal_secrets/roster_backup_20261007__*` 삭제 시점을 대표님이 결정.
