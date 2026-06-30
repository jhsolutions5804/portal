# 0.4. 구조 인덱스 — 전체 앱 · Firestore 컬렉션

> Firebase 프로젝트: `p4ph2-fab-506a7` (전 앱 공용)
> 최초 작성: 2026-07-01 · 작성: 춘식이(Claude)

---

## 앱 파일 구조

```
portal/
├── index.html           포털 메인 (로그인·모듈 임베드·조직도·관리)
├── outlook-auth.html    Outlook OAuth2 콜백
├── gihoek/index.html    기획 (영업·정산·회계)
├── hr/index.html        인사 (급여·계약·근태)
├── edoc/index.html      전자결재
├── pjt/index.html       P4 Ph2 FAB
├── pjt_ph4/index.html   P4 Ph4 SUP
├── scripts/             Python 스크립트 (Firestore 작업용)
├── docs/                문서
└── backup/              버전 백업
```

---

## Firestore 컬렉션 맵

### 포털·인증
| 컬렉션 | 용도 |
|--------|------|
| `portal_users/{uid}` | 사용자(인증·권한·조직도). status, name, rank, dept, phone, email, empNo, admin, perms, dailyViewTargets |

### 인사 (hr)
| 컬렉션 | 용도 |
|--------|------|
| `workers/{id}` | 근로자 명부 |
| `payslips/{wid}/months/{month}` | 급여명세서 (netPay, grossPay 등) |
| `labor_contracts/{wid}/contracts/{id}` | 근로계약서 |
| `annual_contracts/{wid}/contracts/{id}` | 연봉계약서 |
| `company_settings/signatures` | 회사 서명·도장 |

### 기획 (gihoek)
| 컬렉션 | 용도 |
|--------|------|
| `gihoek_projects` | 프로젝트 |
| `gihoek_companies` | 거래처 (발행처/수신처, 담당자) |
| `gihoek_estimates` | 견적 |
| `gihoek_settlements` | 정산 (대금청구서/지급예정서) |
| `gihoek_expenses` | 회계 비용 (수동 + 급여배분 + 용역비연동) |

### 전자결재 (edoc)
| 컬렉션 | 용도 |
|--------|------|
| `edoc_daily` | 업무일지 |
| `edoc_leave` | 연차신청서 |
| `edoc_resign` / `edoc_cert` / `edoc_purchase` / `edoc_expense` | 퇴직원서/재직증명서/구매품의서/지출결의서 |

### PJT 관리 (pjt / pjt_ph4)
| 컬렉션 | 용도 |
|--------|------|
| `pjt_workers_fab` / `pjt_workers_ph4` | 현장 기술인 명단 |
| `user_schedules` | 일정 (주간·캘린더) |
| `daily_reports_{날짜}` | 일별 업무보고 |
| `daily_report_docs/{날짜}` | 일별 종합 보고 문서 |
| `worker_manday/{기간}` | 출역·공수 |
| `progress_checks_{날짜}/{zoneId}` | 공정 체크 |

---

## 앱 간 데이터 연동

| 연동 | 내용 |
|------|------|
| hr → gihoek | 급여명세서(`payslips`)·근로자(`workers`)를 회계 급여배분이 읽음 (N10-2) |
| gihoek 내부 | 지급예정서(`gihoek_settlements`) 완결 → 회계 직접비 자동 반영 (N10-1) |
| edoc → pjt | 연차(`edoc_leave`)를 PJT 주간/캘린더가 표시 |
| 전 앱 → portal | `portal_users` 기반 인증·권한·조직도 공유 |

---

## 문서 번호 체계

| 번호대 | 영역 |
|--------|------|
| 0.x | 기반(컨셉·규칙·인증·구조) |
| 1.x | 기획 |
| 2.x | 인사 |
| 3.x | 전자결재 |
| 4.x | PJT 관리 |
| 5 | 조직도 |
| 6 | Portal 관리 |
| 7.x | 개발 로그 |
