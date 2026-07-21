# 7_3_log_hr r10b
> 이전: 7_3_log_hr_r10a.md

}
```

---

## 급여명세서 공제내역 직접 수정 + 조회 보존 (`14276a84`, `a744f808`, 2026-06-29)

### 기능 1 — 공제내역 직접 수정
- 6개 항목 input 필드로 교체 (자동계산값 기본)
- 수정 시 공제계·실지급액 즉시 재계산
- 근로자/기준월 변경 시 초기화

### 기능 2 — 조회/출력 시 저장값 보존
- `psViewDetail()`에서 저장된 공제값을 `ps._pension` 등으로 세팅
- `psPreview()` (출력)에서 저장된 값 그대로 표시

---

## 초과근로 사유(reason) 필드 추가 (2026-07-21)

### 배경
대표님 요청 "초과근로 상신 시 사유 작성할 수 있게"에 대응. 처음엔 인사 앱(hr/index.html)의 초과근로 관리자 직접입력 탭을 수정했으나, 실제 의도한 화면은 전자결재(edoc)의 "초과근로 작성/상신" 폼이었음(스크린샷으로 확인 후 정정). 최종적으로 두 화면 모두에 사유 필드를 추가.

### hr/index.html 변경 내용
- PC 뷰(`renderOvertimePC`): 입력폼에 `<textarea id="ot-pc-reason">` 추가, `otPcSave()`에서 `reason` 저장 후 필드 초기화
- PC 직원 상세 테이블(`otPcShowPersonDetail`): 사유 컬럼 추가 (긴 텍스트 말줄임 + title 툴팁)
- 모바일 입력폼(`renderOvertimeAdd`): 사유 필드 추가, `otSave()`에서 저장
- 모바일 직원별 조회(`otLoadPersonDetail`) / 전체현황 날짜별 상세(`otLoadSummary`): 사유 컬럼 추가
- 수정 폼(`renderOvertimeEdit`, PC·모바일 공용): 사유 필드 추가, 기존값 로드, `otUpdate()`에서 저장
- `otEsc()` 헬퍼 신규 추가: 사유 등 자유 입력 텍스트 HTML 이스케이프 (기존엔 이런 이스케이프 함수가 없었음)
- Firestore `overtime/{id}` 스키마에 `reason`(string, 선택) 필드 추가. 기존 데이터는 없어도 "-"로 표시되어 마이그레이션 불필요

### edoc/index.html 변경 내용 (상세는 `7_4_log_edoc.md` 참조)
- 초과근로 상신 폼에 사유 텍스트영역 추가 → `edoc_overtime` 저장, 승인 시 인사 `overtime` 컬렉션 연동에도 `reason` 함께 전달

### 문서 정정 (부가 발견)
- `docs/2_4_hr_overtime_r2.md`가 실제 코드와 다른 스키마(`pay`·`hourlyWage`)를 기록하고 있던 것을 발견 → 현재 코드 기준(`amount`·`rate`)으로 정정, r3으로 갱신
- `hr/2_4_hr_overtime_r2.md`(같은 이름의 중복 파일, `hr/` 폴더 내 위치)도 함께 갱신했으나 정식 문서 위치는 `docs/` 폴더가 맞음 — 추후 중복 파일 정리 필요(미해결 이슈로 남김)

### 검증
- `node --check`로 hr(non-module)/edoc(module, .mjs 추출) 스크립트 문법 검증 통과
- portal-test 우선 배포 → 대표님 확인("확인됐어") → production 배포

### 운영 커밋
- portal-test: `hr/index.html` `b22d444`, `edoc/index.html` `859877f`
- production: `hr/index.html` `bc130cd`, `edoc/index.html` `820f134`, `index.html`(버전주석) `5ed6897`
- 백업: `backup/v2.6.1/hr/index.html`, `backup/v2.6.1/edoc/index.html`
