# JH Solutions 포털 — 문서 인덱스

> 최초 작성: 2026-06-26 · 최종 수정: 2026-07-04(r10) · 모바일 UI 통합(v2.0.0) 반영 · 작성: 춘식이(Claude)

---

## 0. 기반 문서

| 파일명 | 내용 |
|--------|------|
| `0_ground_rule_r9.md` | Ground Rule, 용어 정의, 업데이트 절차, Semantic Versioning |
| `0_update_algorithm.md` | 업데이트 알고리즘 상세 절차 |
| `0_1_portal_concept.md` | 포털 concept, structure |
| `0_2a_portal_rule_r2.md` · `0_2b_portal_rule_r2.md` | 포털 기본 rule (a/b 분할) |
| `0_3_portal_auth_r2.md` | 포털 인증 구조 |
| `0_4_structure_index.md` | 구조 인덱스 (전체 앱·컬렉션 목록) |

---

## 1. 기획

| 파일명 | 내용 |
|--------|------|
| `1_0_gihoek_home_r2.md` | 기획 홈 |
| `1_1_gihoek_project.md` | 프로젝트 |
| `1_2_gihoek_company.md` | 거래처 |
| `1_3_gihoek_estimate_r3.md` | 견적 |
| `1_4_gihoek_settle.md` | 정산 |
| `1_5_gihoek_account.md` | 회계 (외상거래·상세내역 필터·등록창 중앙정렬 r2) |

---

## 2. 인사

| 파일명 | 내용 |
|--------|------|
| `2_0_hr_home_r3.md` ~ `2_7_hr_leave_status_r2.md` | 인사 각 기능 (홈·명부·노무연간·연차·연장·급여명세·퇴직·휴가현황) |

---

## 3. 전자결재

| 파일명 | 내용 |
|--------|------|
| `3_0_edoc_home_approve.md` · `3_1_edoc_daily_leave.md` · `3_3_edoc_docs.md` | 전자결재 각 기능 |

---

## 4. PJT 관리

| 파일명 | 내용 |
|--------|------|
| `4_0_pjt_home.md` | PJT 홈 — **통합 캘린더 레이아웃 4.4.0** (카드 가로스크롤·전체폭·달력, 날짜별 일정+업무지시) |
| `4_1_pjt_fab.md` | P4 Ph2 FAB — 홈·오늘·주간(좌우이동)·캘린더(등록/수정·년월점프)·등록자 자동 (4.4.0) |
| `4_1_pjt_fab_attend_progress.md` | P4 Ph2 FAB — 근태(출역·공수 일괄 4.4.0)·공정 · **공정표 PPT 상세 6P·설치진행도·섹터공정율(4.5.1)** |
| `4_2_pjt_sup.md` | P4 Ph4 SUP — FAB 동일 반영 |

---

## 5. 조직도 / 6. Portal 관리

| 파일명 | 내용 |
|--------|------|
| `5_org_chart.md` | 조직도 |
| `6_portal_admin_r2.md` | Portal 관리 |
| `6_expense_upload_log.md` · `expense_upload_routine.md` | 경비 업로드 로그·루틴 |

---

## 7. 개발 로그

| 파일명 | 내용 |
|--------|------|
| `7_0_log_2026-07-02_session.md` | **2026-07-02 세션 종합 로그** (운영 배포·Firebase 격리·트러블슈팅) |
| `7_1_log_portal_r4a.md` ~ `7_7_log_mobile_r1.md` | 모듈별 개발 로그 (portal·gihoek·hr·edoc·pjt·조직/portal관리·모바일통합) |

---

## 8. 모바일 (m/)

| 문서 | 내용 |
|---|---|
| `8_0_mobile_r1.md` | 모바일 UI 통합 — UA 분기, m/ 앱 7종, PJT 모바일(공정·일정·근태), **업무지시/보고 데이터 구조 확정본** |

---

## 세션 요약 — 2026-07-04 (r10)

**모바일 UI 통합 (v2.0.0)**. PC/모바일 UA 기준 분기(PC 무변경) + `m/` 앱 7종(home·gihoek·hr·edoc·admin·account·pjt). PJT 모바일: 공정 실연동(FAB/SUP, calcZone PC값 일치), 일정 캘린더(오늘 자동선택·날짜별 일정+업무지시/보고), 근태(날짜이동·출역토글). 공정 시작일 `pjt_settings`에서 자동조회. **업무지시/보고 경로 정정**: `daily_report_docs`→실제 `daily_reports_{날짜}`/`ph4_daily_{날짜}`(text/name/time/ts). `preview/` 정리. 백업 `backup/v2.0.0/`. **미진행**: 하루 넘기는 일정 완료체크 단일화(→ `7_7_log_mobile_r1.md`).

---

## 세션 요약 — 2026-07-02 (r7)

**PJT 홈 캘린더 개편 + 로그인 자동반영 + 공사일보 이관 + Firebase 격리 완료 (테섭 검증 → 운영 배포 완료)**

| 영역 | 버전 | 주요 변경 |
|------|------|-----------|
| PJT 관리 | 4.3.0 → **4.4.0** | 포털 PJT홈 통합 캘린더(카드 가로스크롤·전체폭·달력확대, 날짜별 일정+업무지시), 주간 좌우 2주 이동, 월간 일정 CRUD·년월 점프, 근태 출역/공수 일괄, 일정 등록자 로그인 자동반영 |
| 회계 | 1.5.x → **r2** | 결제수단 외상거래, 상세내역 필터(날짜·항목·거래처), 등록창 중앙정렬 |
| 공사일보 | 신규 이관 | 별도 저장소(p4ph2-fab-workspace) → `portal/daily-report/` 편입, 작성자 로그인 자동반영 |
| 인프라 | — | **테섭 Firebase 격리 완료**(portal-test-6e0ff 전환), **`.nojekyll` 추가**(빌드 실패·지연 해결), 로그인 계정 localStorage 공유 |

**운영 배포**: index.html·pjt·pjt_ph4·daily-report(+data.js)·.nojekyll — 운영 Firebase(p4ph2-fab-506a7) 유지, 테스트 설정 혼입 없음 확인.

**주요 트러블슈팅**: GitHub Pages 빌드 반복 실패(원인=`.nojekyll` 부재로 인한 Jekyll 오류) → `.nojekyll`로 해결. 캘린더 격자 미표시 → 요소 인라인 스타일로 격자 고정.

**상세**: `7_0_log_2026-07-02_session.md`

---

## 세션 요약 — 2026-07-03 (r9)

**공정표 PPT 상세 6P 신설 + 지급내역 직접수정 (테섭 검증 → 운영 배포 완료)**

| 영역 | 버전 | 주요 변경 |
|------|------|-----------|
| 공정표 PPT | 4.5.0 → **4.5.1** | 섹터별 상세 6P(전일/금일/누계/증감), 설치 진행도 `instBarPct` 반영(2p와 동일), 헤더 섹터 전체 공정율(+전일대비) |
| 급여명세서 | r3 → **r4** | 지급내역 직접 수정(공제와 동일 오버라이드, PC 전용) |
| 백업 | v1.2.0 → **v1.3.0** | pjt·hr index.html |
| 인사 문서 | 2_0 r3a | 구 정산도우미 가이드 대조 → portal 문서 유일 누락분(PDF 출력 규격) 보완, administrator 삭제 가능 상태 |

**운영 커밋**: pjt `16e9ada9`·`285f6ee1` / hr `8bb7b1c0`
