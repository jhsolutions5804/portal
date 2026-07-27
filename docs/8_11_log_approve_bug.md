# 8_11 · 관리자 대신승인 시 결재 미반영 — 진짜 근본 원인 발견·수정 (r1)

**작업일**: 2026-07-26
**대상**: `edoc/index.html`, `debug/overtime_check.html`(신규)
**요청 계기**: 대표님 — "전자결재에서 승인한 정다애 3시간, 이한영 2시간이 인사에서는 조회가 안 돼. log 조회 해봐."

## 진행 경위
1. 07-24 self-heal이 있는데도 여전히 반영 안 됨 → Firestore를 여기서 직접 못 보고, 대표님이 로컬 스크립트도 못 돌리셔서 **읽기 전용 진단 웹페이지**(`debug/overtime_check.html`) 제작
2. 1차 시도: Google 로그인으로 만들었다가 "로그인이 안 된다" 피드백 → 포털이 ID/PW 로그인 방식임을 재확인, 로그인 폼 교체
3. 진단 페이지 스크린샷으로 실제 원인 확인: `edoc_overtime` 4건 전부 `status: 'pending'`(승인이 실제로 반영된 적이 없었음)

## 원인
- 승인 버튼 노출 조건(`docDetail`의 `canApprove`)에는 관리자 예외가 있어 버튼은 보였지만
- 실제 승인 처리(`docApprove`의 `isMyStep`)에는 관리자 예외가 없어서, 관리자(대표님)가 결재라인에 지정된 본인(김종화)이 아닌 상태로 대신 승인하면 결재라인이 하나도 갱신되지 않고 저장이 실패, `status`가 계속 `pending`으로 남음
- **초과근로뿐 아니라 모든 문서 타입에서 관리자 대신승인 시 공통으로 발생하던 버그**

## 수정
`docApprove()`의 대상 단계 판단을 순번 기반 단일 단계 타겟팅으로 재작성:
1. uid/이름 정확히 일치 + 순번상 차례 → 1순위
2. 없으면 관리자가 순번상 차례가 된 단계를 대신 처리 → 2순위
3. `targetIdx` 하나만 확정 — 다단계 결재라인(결재1→결재2)에서 관리자가 눌러도 여러 단계 동시승인되는 사고 방지

## 검증
- `node --check` 통과

## 배포
- 커밋: `edoc/index.html` `4f0eace`, `index.html`(버전주석)
- 백업: `backup/v2.6.7/edoc/index.html`
- 문서: `docs/3_4_edoc_overtime_r1.md`(r5), `docs/3_0_edoc_home_approve.md`(r3, 범용 결재 로직 문서화)
- 진단 도구: `debug/overtime_check.html` (읽기 전용)

## 다음 확인 필요
대표님이 정다애·이한영 등 대기중 4건을 재승인 후 인사에 정상 반영되는지 확인 예정.

## 여전히 미해결로 남은 이슈
`edoc/index.html` 결재함(`loadApproveData`)의 `DOC_TYPES`에 `'overtime'` 누락 (2026-07-23 발견, `docs/3_0_edoc_home_approve.md` 참조)
