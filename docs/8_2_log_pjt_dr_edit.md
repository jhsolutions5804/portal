# 8_2 · PJT 공사일보 조회 수정/삭제 (r1)

**작업일**: 2026-07-08
**대상**: `pjt/index.html`(FAB) · `pjt_ph4/index.html`(SUP)
**요청**: 작성해 놓은 공사일보 조회 시 수정/삭제 가능하게

## 변경 내용
- 공사일보 **상세 모달**에 편집/삭제 기능 추가 (기존 조회·PDF는 유지)
- 상세 하단 버튼: 보기모드(📄PDF / ✏️수정 / 🗑삭제 / 닫기) ↔ 편집모드(💾저장 / 취소) 토글
- 수정 가능 필드: 작성자·금일작업·명일예정·투입인원·사용장비·특이사항
- 고정 필드: 현장명·작성일자(문서 키 근거) → 회색 read-only
- XSS 방지용 HTML 이스케이프(`_drEsc`) 추가

## 컬렉션
- FAB: `daily_report_docs` / SUP: `ph4_reports` (문서 ID = 날짜키)
- 수정: `setDoc(..., {merge:true})` + `updatedAt` 타임스탬프
- 삭제: `deleteDoc` (confirm 확인 후, 복구 불가 안내)

## 신규 함수
- module: `window._fbUpdateReportDoc(dateKey, patch)`, `window._fbDeleteReportDoc(dateKey)`
- UI: `renderDRView`, `toggleDRBtns`, `editDRDetail`, `cancelDREdit`, `saveDRDetail`, `deleteDRDetail`
- `openDRDetail` 리팩토링 → `renderDRView` 재사용

## 검증
- `node --check`: 두 파일 전 script 블록 정상
- jsdom 흐름(뷰→편집→저장→취소→삭제): FAB 19/19, SUP 19/19 통과
- production/test diff: Firebase config·링크 경로 외 수정/삭제 코드 완전 동일

## 배포
- test(portal-test): FAB `a13f0f68` / SUP `c4e58522`
- production(portal): FAB `a0942203` / SUP `18febd57`
- backup: **v2.2.0** (pjt·pjt_ph4 index.html)
