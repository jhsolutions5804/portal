# 4.2. PJT 관리 — P4 Ph4 SUP

> 앱: `portal/pjt_ph4/index.html` · 워커 컬렉션: `pjt_workers_ph4`
> 현장: 귀뚜라미범양냉방 · EHU 설치
> 최초 작성: 2026-07-01 · 작성: 춘식이(Claude)

---

## 개요

P4 Ph4 SUP는 **P4 Ph2 FAB(4.1)와 동일한 코드 베이스**이다. 6개 탭(홈·오늘·주간·캘린더·근태·공정) 구조와 동작이 모두 같으며, 차이는 다음뿐이다:

| 항목 | FAB (4.1) | SUP (4.2) |
|------|-----------|-----------|
| 앱 경로 | `portal/pjt/` | `portal/pjt_ph4/` |
| 워커 컬렉션 | `pjt_workers_fab` | `pjt_workers_ph4` |
| 현장 | FCU 설치 | EHU 설치 |

---

## 탭 구성 (4.1과 동일)

| 탭 | 내용 | 컬렉션 |
|----|------|--------|
| 4.2.0 홈 | 대시보드 | — |
| 4.2.1 오늘 | 업무보고·일정 | `daily_reports_{날짜}`, `daily_report_docs` |
| 4.2.2 주간 | 2주 일정 | `user_schedules`, `edoc_leave` |
| 4.2.3 캘린더 | 월 캘린더 | `user_schedules` |
| 4.2.4 근태 | 출역·공수 | `worker_manday` |
| 4.2.5 공정 | 공정률 | `progress_checks_{날짜}` |

> 각 탭의 상세 동작은 4.1(FAB) 문서를 참조한다. 데이터 컬렉션 중 `user_schedules`·`daily_reports`·`worker_manday`·`progress_checks`는 공용이거나 동일 명명 규칙을 따른다.

---

## 공통

- Firebase 프로젝트: `p4ph2-fab-506a7` (포털 공용)
- 포털 임베드 시 사이드바·탭바 숨김, 자체 상단 탭바 사용
