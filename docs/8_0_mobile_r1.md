# 8.0. 모바일 UI 통합 (r1)

> Firebase 프로젝트: `p4ph2-fab-506a7` (PC와 공용)
> 작성: 2026-07-04 · 작성: 춘식이(Claude) · 릴리스: v2.0.0

---

## 개요

포털에 **모바일 전용 화면**을 추가했다. 기존 PC 화면(사이드바+iframe)은 그대로 두고, 모바일 접속 시 별도 화면(`m/` 폴더)으로 분기한다.

- **분기 기준: User-Agent** (픽셀 폭 아님). `index.html`의 `showApp()`에서 `/Mobi/i.test(navigator.userAgent)`이면 `m/home.html`로 이동. → 폴더블(폴드7) "데스크톱 사이트 보기"는 PC 화면으로 정상 표시됨.
- 로그인·권한은 `index.html`이 처리하고, 로그인 시 `localStorage.jh_login_perms`(JSON: perms, admin, uid, name, dept, rank)를 저장 → 모바일 앱이 이를 읽어 권한 분기.
- 모바일 앱은 같은 origin(`portal.jhsol.kr/m/`)이라 `localStorage`(jh_login_full/name/perms, fabls_/ph4ls_ 등)와 Firestore를 PC와 공유.

---

## 모바일 앱 파일 (`portal/m/`)

| 파일 | 내용 |
|---|---|
| `m/home.html` | 모바일 홈. 4개 대형 타일(기획=파랑·인사=주황·전자결재=보라·PJT=초록) + 조직도/Portal관리(admin) + 아바타→계정. 권한 게이팅(perms 없는 섹션 🔒). |
| `m/gihoek.html` | 기획 SPA. 프로젝트/거래처/견적/정산/회계 (list→detail). |
| `m/hr.html` | 인사 SPA. workers(사번순)/overtime/edoc_leave. |
| `m/edoc.html` | 전자결재 SPA. 결재함/업무일지/연차신청서, 상태 배지. |
| `m/admin.html` | 조직도(portal_users by dept) + Portal관리(계정 권한). `?v=org|admin`. |
| `m/account.html` | 로그인 계정 정보 (jh_login_full + portal_users). |
| `m/pjt.html` | PJT 앱 (아래 상세). |

---

## PJT 모바일 (`m/pjt.html`)

홈(FAB/SUP 카드) → 현장 선택 → 서브탭 **공정 / 일정 / 근태**.

### 공정 (progress) — 실데이터 연동
- **계산식 검증됨**(PC 화면값 3F FIZ 51.3%, 전체 10.9%와 일치):
  - 섹터 % = `totalChecked / (섹터장비수 × 체크컬럼수) × 100`
  - 전체 공정율 = `Σ각섹터 totalChecked / Σ각섹터 mx`
  - "설치 N/total" = 설치항목(installCols) **전부** 완료된 장비 수(instDone). 단, 개별 설치 체크는 totalChecked에 포함.
- **데이터 소스(현장별)**:
  - FAB: 컬렉션 `progress_checks_{날짜}`, localStorage `fabls_eq_ck_`, checkCols 8개(반입·입고검사·내진스토퍼·다이크·실링·동판·결선·시공검측), installCols 5개, 섹터 6개(183대), PAST(하드코딩 2026-06-17~20 fiz).
  - SUP: 컬렉션 `ph4_progress_{날짜}`, localStorage `ph4ls_eq_ck_`, checkCols 4개(반입·입고검사·내진스토퍼·시공검측), installCols 1개, 섹터 4개(11대), PAST 없음.
  - 문서ID=zoneId, 필드 `.checks = {장비_컬럼: true}`.
- **누적 로딩**: 시작일~오늘 각 날짜 컬렉션을 getDocs로 병합 + PAST + 오늘 localStorage.
- **시작일**: `pjt_settings/p4ph2`(FAB)·`pjt_settings/p4ph4`(SUP)의 `startDate`를 Firestore에서 자동 조회(없으면 넉넉한 기본값). → PC 설정과 자동 일치.
- **모바일 체크**: 섹터 카드 펼침→장비별 체크 테이블. **오늘 날짜만 수정 가능**(과거는 읽기전용, 회색). 저장은 PC와 동일 방식(`{coll}{오늘}/{zoneId}`의 checks). 날짜별로 취합됨.

### 일정 (sched) — 캘린더
- 월간 캘린더. 일정 있는 날 점(●). 진입 시 **오늘 자동 선택**.
- 날짜 클릭 → 하단에 **일정 + 업무지시/보고** 동시 표시(PC PJT홈 방식).
- 일정 데이터: `user_schedules`(FAB)/`ph4_schedules`(SUP). 필드 sdate/edate/stime/etime/text/tag/pjtName. 태그색 PC와 동일.
- 일정 카드 클릭 → 상세 화면.

### 근태 (attend)
- **날짜 이동 네비**(‹ › 오늘)로 지난 출역·공수 조회. 오늘만 출역 체크 가능(과거 읽기전용).
- 기술인 명단: `pjt_workers_fab`(FAB)/`pjt_workers_ph4`(SUP), 필드 id/name/role/order/active.
- 출역: `worker_attendance/{날짜}`(FAB)/`ph4_attendance/{날짜}`(SUP), `{checks:[wid들]}`.
- 공수: `worker_manday/{날짜}`(FAB)/`ph4_manday/{날짜}`(SUP), `{md:{wid:값}}`. (표시 전용, 입력 미구현)

---

## 업무지시/보고 데이터 구조 (중요 · 확정본)

**PC·모바일 공통.** 여러 번 혼동됐던 부분이라 확정 기록:

- **저장 위치**: PJT 모듈 "오늘/날짜" 탭 우측 "업무지시 및 보고" 패널에서 등록.
  - FAB: 컬렉션 **`daily_reports_{날짜}`** (예: `daily_reports_2026-07-10`)
  - SUP: 컬렉션 **`ph4_daily_{날짜}`**
  - 각 보고 = `addDoc`으로 추가되는 개별 문서. 필드 **`text`(내용)·`name`(작성자)·`time`(시각)·`ts`(serverTimestamp)**.
- **(주의) 아님**: `daily_report_docs`·`ph4_reports`(문서ID=날짜, instruction/briefText)는 **틀린 경로**였음. `daily-report/` 모듈은 공사일보(count/equip/remarks)로 별개.
- **읽기(홈 요약 패널)**: 최근 21일 + 미래 21일 범위로 각 날짜 컬렉션 훑어 최신순 표시. (미래 날짜 등록분 누락 방지)
- **읽기(캘린더 날짜별·모바일)**: 선택 날짜의 `daily_reports_{날짜}`/`ph4_daily_{날짜}` getDocs.

---

## 기타 정리

- `preview/` 폴더(옛 모바일 미리보기 15개) 삭제 → `m/`으로 일원화.
- `scripts/inspect_reports.py` 추가: Firestore 컬렉션 실조회 스크립트(대표님 로컬 실행용, admin SDK 키 필요).
- **주의(개발)**: 근태 `attDate` 초기화가 `todayStr` 정의보다 앞서면 TDZ로 페이지 로드 불가 → 초기화는 정의 이후 또는 직접 계산. mock 초기실행 테스트로 검출 가능.

---

## 관련 커밋 (2026-07-04)
모바일 앱 구축 → 공정 실연동(daf758f1) → 여백+체크(4a07386a) → SUP 공정(e50d0884) → 시작일 자동조회(2f7502c8) → 근태(db039e42) → 근태 날짜이동+TDZ수정(e4844066) → 업무지시/보고 실구조 수정(PC 3d5c91d0 / 모바일 24ad0c6b).
