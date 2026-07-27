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

## 보안 아키텍처 — 3중 방어 (2026-07-27 완성)

대표님 요청: "외부 유입이 완전히 단절된 폐쇄적인 workspace" — 아래 3개 레이어가 모두 갖춰져야 완성됨.

| 레이어 | 내용 | 상태 |
|--------|------|------|
| ① 화면(UI)단 | 모든 서브 메뉴(`pjt_manday`, `pjt`, `pjt_ph4`, `pjt_light`, `hr`, `edoc`, `gihoek`)에 로그인+`portal_users`(`status==='approved' && (admin \|\| perms.*)`) 검증 게이트 적용. URL 직접 접근·`?via=portal`·`?admin=1` 등 파라미터 우회 전부 차단 | ✅ 완료 (코드 배포, `7_11_log_pjt_5_1_0.md` 등 참고) |
| ② 로그인 방식 | Firebase Auth "Sign-in method"를 이메일/비밀번호만 남기고 그 외(Google 등) 전부 비활성화. 계정은 관리자만 생성 가능, 아이디는 `@jhsol.kr`로 자동 고정(`DOMAIN` 상수), 승인제(`portal_users.status`) | ✅ 완료 (콘솔 작업, 본섭·테섭 둘 다) |
| ③ 데이터(Firestore 보안 규칙) | 로그인 안 됐거나, 승인 안 됐거나, `@jhsol.kr` 계정이 아니면 Firestore 자체가 읽기/쓰기 거부. 브라우저 개발자도구로 SDK를 직접 호출해도 막힘(최종 방어선) | ✅ 완료 (콘솔에서 규칙 게시, 본섭·테섭 둘 다, 게시 후 정상 로그인·데이터 조회 확인함) |

**Firestore 규칙 요지**: `portal_users/{uid}`는 본인만 읽기(로그인 승인 체크용)·관리자만 쓰기, 그 외 전체 컬렉션(`match /{document=**}`)은 승인된 `@jhsol.kr` 계정만 읽기/쓰기. 향후 신설되는 컬렉션도 별도 규칙 추가 없이 자동으로 보호됨.

**남은 참고사항**:
- Firestore 규칙은 앱 코드가 아니라 Firebase 콘솔에서 직접 관리 — 이 저장소엔 `firestore.rules` 파일이 없으므로, 규칙 변경 시 항상 콘솔에서 직접 게시해야 함(추후 Firebase CLI로 버전관리 전환 검토 가능)
- 규칙은 승인 여부까지만 구분하고 모듈별 세부 권한(`perms.pjt`/`perms.hr` 등)까지는 구분하지 않음 — 세부 권한 구분은 계속 앱(UI)단에서 담당


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

