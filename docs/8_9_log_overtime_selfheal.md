# 8_9 · 초과근로 edoc↔hr 자동연동 실패 대응 — self-heal 도입 (r1)

**작업일**: 2026-07-24
**대상**: `hr/index.html`
**요청 계기**: 대표님 — "얼마 전에 2명 초과근로 승인을 했는데 인사에는 반영이 안 됐더라고"

## 진행 경위
1. 승인 시 자동연동 코드(`docApprove`)를 재검토 — 로직상 문제는 안 보임
2. 진단을 위해 `scripts/check_overtime_link.py` 작성, 대표님께 로컬 실행 안내 → 대표님이 비개발자라 실행 불가("나 이거 하나도 모르겠어서 못하겠어")
3. Chrome 확장 연결 여부 확인(`list_connected_browsers`) → 연결된 브라우저 없음 → 브라우저 자동화로 대신 확인하는 것도 불가
4. **원인 규명을 포기하고 자동 복구(self-heal) 방식으로 전환**: 인사 초과근로 탭 진입 시마다 누락분을 자동으로 채워 넣도록 구현

## 수정 내용
- `hr/index.html`: `window.otSyncFromEdoc()` 신규 함수 추가
  - `edoc_overtime`에서 `status==='approved' && !linkedToOvertime` 문서를 찾아 `overtime`에 자동 추가 + 플래그 마킹
  - `renderOvertimeMain()`을 async로 변경, 진입 시 `await otSyncFromEdoc()` 선실행
  - 콘솔 로그만 남기고 alert 없음 — 사용자 개입 불필요

## 사고 및 복구
`backup/v2.6.3/hr/index.html` 백업 경로가 **다른 세션(hr payslip 작업)이 이미 사용 중이던 버전 번호와 충돌** → 실수로 기존 백업 덮어씀 → git blob API(`GET /git/blobs/{sha}`)로 원본 복구, 신규 백업은 `backup/v2.6.4/hr/index.html`로 재배치. 향후 백업 PUT 전 반드시 GET으로 기존 파일 유무 확인하기로 함.

## 부수 발견 (미해결)
`edoc/index.html`의 결재함(`loadApproveData`) `DOC_TYPES` 배열에 `'overtime'`이 빠져있어, 초과근로는 결재함에 절대 노출되지 않음. `TYPE_LABEL`에는 이미 등록되어 있어 의도했던 것으로 보이나 실제 반영이 안 된 상태 — 다음 세션 과제로 남김.

## 검증
- `node --check` 문법 검증 통과
- 대표님 승인("응 적용해") 후 **테스트서버 생략, 본섭 직접 배포**

## 운영 반영
- 커밋: `hr/index.html` `d6db6b0`, `index.html`(버전주석)
- 백업: `backup/v2.6.4/hr/index.html`
- 문서: `docs/2_4_hr_overtime_r2.md`(r4), `docs/3_4_edoc_overtime_r1.md`(r4), `docs/7_3_log_hr_r10b.md`
- 진단 스크립트(참고용, 필수 아님): `scripts/check_overtime_link.py`
