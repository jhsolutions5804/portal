# 2.1. 인사 — 근로자 명부

> Firestore 컬렉션: `workers`
> 최초 작성: 2026-06-26 · 최종 수정: 2026-06-27 · 작성: 춘식이(Claude)

---

## Firestore 스키마

```js
workers/{workerId}:
{
  empNo:       string,    // 가입연도2자리 + 연도순번3자리 (예: 26001)
  name:        string,
  jumin:       string,    // 주민번호 13자리
  phone:       string,
  address:     string,
  dept:        string,
  rank:        string,
  job:         string,
  empType:     'field' | 'office',
  hireDate:    string,    // YYYY-MM-DD
  bankAccount: string,
  portalUid:   string,    // portal_users UID (연동 키)
  registeredAt: string    // ISO 문자열
}
```

**workerId 형식**: `{이름}_{주민번호 13자리}` (예: `홍길동_9001011234567`)

---

## 화면 레이아웃 (D1 개선, 2026-06-27)

### 목록 화면 (PC 기준)
- 탭 진입 즉시 **근로자 명단 전체 테이블**로 표시 (기존 등록/조회 선택 화면 제거)
- **우측 상단에 `➕ 신규 등록` 버튼** 별도 배치
- `max-width: 1100px` — PC 환경에 맞게 가로 활용
- 테이블 컬럼: 사원번호·이름·소속·직급·구분·생년월일·휴대폰·근로계약·연봉계약·포털 연동·삭제

### 포털 연동 표시
- 🔗 초록 뱃지: `portalUid` 있음 (포털 계정 연동)
- 회색 `-` 뱃지: 미연동

---

## 신규 등록 — portal_users 드롭다운 연동

신규 등록 폼 상단에 **포털 가입자 목록 드롭다운** 제공:
1. `portal_users` 컬렉션 전체 로드
2. 이미 `workers.portalUid`에 연동된 계정은 목록에서 **자동 제외**
3. 드롭다운 선택 시 → 이름·직급·부서 **자동 채움** + `portalUid` 저장
4. 포털 미연동 근로자는 "직접 입력" 선택 후 수동 입력

```js
// 드롭다운 선택 핸들러
window.rosterPortalUserSelect = (uid) => {
  const u = portalUsersList.find(x => x.uid === uid);
  rosterForm.name  = u.name;
  rosterForm.rank  = u.rank;
  rosterForm.dept  = u.dept;
  rosterForm.portalUid = uid;
  // 화면 필드 자동 반영
};
```

---

## 목록 정렬

- 사번순(empNo) 오름차순
- `(a.empNo||'').localeCompare(b.empNo||'')`
- 적용 위치: renderRosterMain, renderLaborRegister(×3), renderLeaveStatusMain

---

## portal_users 연동

| 공유 필드 | 연동 방식 |
|----------|---------| 
| name, rank, dept, empNo | 포털 계정 생성·수정 시 자동 동기화 |
| portalUid | portal_users의 uid를 workers에 저장 |

**workers 전용 필드**: jumin, hireDate, bankAccount, phone, address, job, empType
→ hr 앱 신규 등록 폼에서 입력

---

## 사번 자동 부여 규칙

```
empNo = 가입연도 2자리 + 해당 연도 순번 3자리
예) 2026년 첫 번째 → '26001'
예) 2026년 세 번째 → '26003'
```

- 같은 연도 최대 empNo + 1, 3자리 zero-padding
- 사원번호 클릭 시 수기 수정 가능

---

## CRUD 주요 함수

| 함수 | 역할 |
|------|------|
| `renderRosterMain()` | 명부 목록 테이블 렌더 (탭 진입 시 바로 표시) |
| `renderRosterRegister()` | 신규 등록 폼 (portal_users 드롭다운 포함) |
| `rosterPortalUserSelect(uid)` | 드롭다운 선택 시 폼 자동 채움 |
| `loadPortalUsers()` | portal_users 컬렉션 로드 및 캐시 |
| `rosterSave()` | workers 저장 (portalUid 포함) |
| `rosterDetail(id)` | 이름 클릭 → 상세/수정 모달 |
| `renderRosterList()` | renderRosterMain() 으로 리다이렉트 |
