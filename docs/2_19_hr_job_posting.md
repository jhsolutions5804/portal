# 2.19. 인사 — 공고 관리 (hr 2.26.0)

> 최종 개정: 2026-10-01 (hr 2.26.0) · 춘식이(Claude) · 대표님 지시로 신설

## 개요
인사 > 공고 관리 탭에서 채용 공고를 등록·수정·마감·삭제하고, 홈페이지(jhsolutions5804.github.io)의 채용 3페이지로 바로 이동한다. 저장된 공고는 홈페이지가 읽어서 보여준다.

## 홈페이지 바로가기 (새 창)
| 버튼 | 대상 |
|------|------|
| 채용 소개 (랜딩) | `careers.html` — 인재상·EVP·복지·채용 프로세스 |
| 채용 공고 | `recruit-jobs.html` — 진행 중 공고 목록·상세 보기 |
| 지원 폼 | `recruit.html` — 지원서 입력(공고별 링크는 `recruit.html?job={공고ID}`) |

## 데이터 — `job_postings/{id}`
- 항목(사람인 공고 양식 순서): `title` `team`(모집분야 태그) · `career` `education` `empType` · `salary` `workTime` `location` · `duties` `requirements` `preferred` `benefits`(줄바꿈=항목) · `process` `documents` `notes` · `startDate` `deadline` · `status`(open 게시 / closed 마감 / draft 임시저장) · `createdAt` `updatedAt`.
- 새 공고 작성 시 `JOB_DEFAULTS`(hr/index.html)의 기본 문구가 자동으로 채워지며 모두 수정 가능(기존 공고는 영향 없음). `benefits`는 비워 둔다 — 공통 복지는 `careers.html` 복지 섹션에 게시.
- 노출 조건(홈페이지): status=open AND 접수 시작일 ≤ 오늘 AND (마감일 없음 OR 마감일 ≥ 오늘). 목록·careers 첫 화면에 진행 중 공고 수 표시.
- 공고 삭제 시 이미 접수된 지원서(`recruit_applicants`)는 유지된다.

## 보안 규칙 (Firestore)
- `job_postings`: 비로그인은 **status=='open' 문서만** get/list, 생성·수정·삭제·전체 조회는 `isAdmin()`만. `isAdminOnlyCollection` 목록에도 포함(catch-all 제외).
- 본섭 규칙 게시 2026-10-01(전/후 백업 `backup/20261001_job_postings/rules/`, 실서버 점검: 비로그인 open 조회 200, 전체 조회·마감 문서·쓰기·삭제 403).

## 홈페이지 파일(별도 레포 jhsolutions5804.github.io)
- `recruit-jobs.html`: 공고 목록(Firestore 조회), 카드 + 상세 보기(핵심 정보·주요업무·자격요건·우대·복지·채용절차·유의사항). 텍스트는 textContent로만 출력(HTML 주입 방지).
- `recruit.html`: `?job=` 공고가 게시 중이면 제목·팀 태그 표시, 아니면 기본 문구.
- `careers.html`: 복지 및 혜택 섹션(자기 개발 지원·사내 문화·보상), 진행 중 공고 수, 채용 프로세스(공고 확인→지원서 접수→서류전형→면접→최종합격·입사).
- 교체 전 원본: `backup/20261001_job_postings/homepage_before/` (테섭 레포).

## 참고
- 사람인에 올려 둔 공고와 홈페이지 공고는 별개로 운영된다(지원자 유입 경로가 나뉨). 홈페이지 지원서는 인사 > 채용 지원자로 들어온다.
- 테섭은 테섭 DB에 연결된 사본(`portal-test/recruit-test/`)을 연다. 본섭 버튼 주소는 `JOB_HOME_BASE`.
