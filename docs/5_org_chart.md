# 5. 조직도

> 위치: 포털 `index.html` — `view-org` 섹션 / `loadOrg()` · 모바일 `m/admin.html` — `renderOrg()`
> Firestore: `portal_users`
> 최초 작성: 2026-07-01 · 작성: 춘식이(Claude)
> 최종 개정: 2026-09-19 (모바일 관리 2.7.0 — 모바일 조직도 정렬 규칙)

---

## 개요

승인된 전 직원(`portal_users` 중 `status==='approved'`)을 부서별로 묶어 표로 보여주는 조직도. 모든 로그인 사용자가 열람 가능(사이드바·더보기 메뉴의 "🏢 조직도").

---

## 진입

- 사이드바 `org` 메뉴 또는 모바일 더보기 → `showView('org')` + `loadOrg()`

---

## 데이터 소스

```js
getDocs(query(collection(db,'portal_users'), where('status','==','approved')))
```

`portal_users/{uid}` 주요 필드: `name`, `rank`, `dept`, `phone`, `email`, `empNo`, `status`, `createdAt`

---

## 부서·직급 정렬 기준

```js
DEPT_ORDER = ['(미지정)','사업본부','현장관리팀','인력배치팀',
              '경영지원본부','경영총무팀','영업기획팀']
RANK_ORDER = ['대표','부사장','차장','과장','대리','사원']
```

- 직원을 `dept`로 그룹핑 (DEPT_ORDER에 없는 부서는 '(미지정)')
- 부서 내 정렬: `empNo` 가나다·숫자순 → empNo 없으면 `createdAt` 순
- 빈 부서는 표시하지 않음

---

## 화면 구성

부서별 카드(`org-dept-card`):
- 헤더: 📂 부서명 + 인원수
- 테이블 컬럼: 사원번호 · 소속 · 이름 · 직급 · 전화번호 · 메일주소

---

## 관련 (직원 상세)

- 관리자는 Portal 관리(`view-admin`)에서 직원 상세(`view-emp-detail`)로 진입 가능 (→ 6. Portal 관리 참조)

---

## 모바일 조직도 (`m/admin.html` · `?v=org`)

PC 표(`loadOrg`)와 별도로 모바일은 카드 목록(`renderOrg`)으로 표시. 데이터는 `portal_users` 실시간 구독.

### 정렬 규칙 (2026-09-19, 모바일 관리 2.7.0)

1. **대표(송지훈) 최상단** — 부서 헤더 없이 카드만 맨 위에 표시. 판별: `name==='송지훈'` 또는 `rank==='대표'`. 부서 수(`N개 부서`)에서는 제외, 전체 인원(`전체 N명`)에는 포함.
2. **부서 순서 고정** — `ORG_DEPT_ORDER = ['사업본부','경영지원본부','경영총무팀','현장관리팀','인력배치팀','guest','미지정']`
   - `dept`가 비었거나 `(미지정)`이면 `미지정`으로 묶음
   - 목록에 없는 부서(예: 영업기획팀)는 `guest` 뒤 · `미지정` 앞에 가나다순
3. **부서 내 사번 순** — `localeCompare(..., {numeric:true})`. 숫자 사번(`22001`)이 문자 섞인 사번(`guest001`)보다 앞. 사번 없는 인원은 부서 맨 뒤. 동일 사번이면 직급 → 이름 순.

> PC 조직도(`loadOrg`)는 별도 `DEPT_ORDER`(위 "부서·직급 정렬 기준")를 유지 — 이번 변경 대상 아님. 두 화면의 부서 순서는 현재 다름.
