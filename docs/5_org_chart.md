# 5. 조직도

> 위치: 포털 `index.html` — `view-org` 섹션 / `loadOrg()`
> Firestore: `portal_users`
> 최초 작성: 2026-07-01 · 작성: 춘식이(Claude)

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
