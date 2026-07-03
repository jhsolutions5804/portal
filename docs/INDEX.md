# JH Solutions 포털 — 문서 인덱스

> 최초 작성: 2026-06-26 · 최종 수정: 2026-07-03(r8) · 작성: 춘식이(Claude)

---

## 0. 기반 문서

| 파일명 | 내용 |
|--------|------|
| `0_ground_rule_r9.md` | Ground Rule, 용어 정의, 업데이트 절차, Semantic Versioning |
| `0_update_algorithm.md` | 업데이트 알고리즘 상세 절차 |
| `0.1_portal_concept.md` | 포털 concept, structure |
| `0.2_portal_rule.md` | 포털 기본 rule |
| `0.3_portal_auth.md` | 포털 인증 구조 |
| `0.4_structure_index.md` | 구조 인덱스 (전체 앱·컬렉션 목록) |

---

## 1. 기획

| 파일명 | 내용 |
|--------|------|
| `1.0_gihoek_home.md` | 기획 홈 |
| `1.1_gihoek_project.md` | 프로젝트 |
| `1.2_gihoek_company.md` | 거래처 |
| `1.3_gihoek_estimate.md` | 견적 |
| `1.4_gihoek_settle.md` | 정산 |
| `1.5_gihoek_account.md` | 회계 (외상거래·상세내역 필터·등록창 중앙정렬 r2) |

---

## 2. 인사

| 파일명 | 내용 |
|--------|------|
| `2.0_hr_home.md` ~ `2.7_hr_leave_status.md` | 인사 각 기능 |

---

## 3. 전자결재

| 파일명 | 내용 |
|--------|------|
| `3.0_edoc_home_approve.md` · `3.1_edoc_daily_leave.md` · `3.3_edoc_docs.md` | 전자결재 각 기능 |

---

## 4. PJT 관리

| 파일명 | 내용 |
|--------|------|
| `4.0_pjt_home.md` | PJT 홈 — **통합 캘린더 레이아웃 4.4.0** (카드 가로스크롤·전체폭·달력, 날짜별 일정+업무지시) |
| `4.1_pjt_fab.md` | P4 Ph2 FAB — 홈·오늘·주간(좌우이동)·캘린더(등록/수정·년월점프)·등록자 자동 (4.4.0) |
| `4.1_pjt_fab_attend_progress.md` | P4 Ph2 FAB — 근태(출역·공수 일괄 4.4.0)·공정 · **공정표 PPT 섹터별 상세 6P(4.5.0)** |
| `4.2_pjt_sup.md` | P4 Ph4 SUP — FAB 동일 반영 |

---

## 5. 조직도 / 6. Portal 관리

| 파일명 | 내용 |
|--------|------|
| `5_org_chart.md` | 조직도 |
| `6_portal_admin.md` | Portal 관리 |

---

## 7. 개발 로그

| 파일명 | 내용 |
|--------|------|
| `7.0_log_2026-07-02_session.md` | **2026-07-02 세션 종합 로그** (운영 배포·Firebase 격리·트러블슈팅) |
| `7.1_log_portal.md` ~ `7.6_...md` | 모듈별 개발 로그 |

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

**상세**: `7.0_log_2026-07-02_session.md`
