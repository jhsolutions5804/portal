# 0.3. 포털 인증 구조

> Firebase Auth 기반 계정·권한 관리
> 최초 작성: 2026-06-26 · 최종 수정: 2026-06-27 · 작성: 춘식이(Claude)

---

## 인증 방식

- Firebase Auth 이메일/비밀번호
- `@jhsol.kr` 도메인 전용

---

## 계정 생성 흐름

```
관리자(대표)가 Portal 관리 메뉴에서 직접 계정 생성
  → Firebase Auth에 계정 생성 (Secondary App 사용)
  → portal_users에 status: 'approved'로 즉시 등록
  → workers 컬렉션에 근로자 명부 자동 생성 (portalUid로 연결)
  → 직원은 바로 로그인 가능
```

> ⚠️ 자동 생성된 workers 문서는 name·rank·dept·empNo만 채워진 상태.
> jumin·phone·address·bankAccount·hireDate 등은 **hr 앱 근로자 명부에서 별도 입력** 필요.

---

## Firestore 스키마

### `portal_users/{uid}`

```js
{
  email:     string,           // id@jhsol.kr
  name:      string,
  rank:      string,           // 대표/부사장/차장/과장/대리/사원
  dept:      string,           // 선택사항
  empNo:     string,           // 가입연도2자리 + 연도순번3자리
  status:    'approved',
  admin:     bool,
  perms: {
    plan:  bool,               // 기획 앱
    hr:    bool,               // 인사 앱
    edoc:  bool,               // 전자결재 앱
    pjt:   bool,               // PJT 업무관리
  },
  _pw:       string,           // btoa(encodeURIComponent(pw))
  createdAt: serverTimestamp,
}
```

### `workers/{workerId}` (마스터)

```js
{
  empNo:       string,
  name:        string,
  jumin:       string,    // 주민번호 13자리 — hr 앱 전용 입력
  phone:       string,
  address:     string,
  dept:        string,
  rank:        string,
  job:         string,
  empType:     'field' | 'office',
  hireDate:    string,
  bankAccount: string,
  portalUid:   string,    // portal_users UID (연동 키)
  signData:    string,    // 개인 서명 base64 (전자결재 연동용)
  registeredAt: string,
}
```

---

## 로그인 흐름

```
로그인 → portal_users/{uid} 조회
  → 문서 없음: "등록되지 않은 계정" → 로그아웃
  → status !== 'approved': 로그아웃
  → approved: enterPortal() 호출
```

**관리자 자동 부트스트랩**: `jh.kim@jhsol.kr` 최초 로그인 시
→ `admin:true`, 모든 `perms:true`로 자동 등록

---

## 각 앱 인증 구조 (포털 경유 / 직접 접근 공통)

```js
onAuthStateChanged(auth, async u => {
  if (!u) { show('login'); return; }

  const via = new URLSearchParams(location.search).get('via') === 'portal';
  if (via) {
    const ps = await getDoc(doc(db, 'portal_users', u.uid));
    if (ps.exists() && ps.data().status === 'approved') {
      enterApp(u); return;
    }
    enterApp(u); return;  // portal 경유면 오류 시에도 허용
  }

  // 직접 URL 접근
  const ps = await getDoc(doc(db, 'portal_users', u.uid));
  if (ps.exists() && ps.data().status === 'approved') {
    enterApp(u);
  } else {
    show('denied');
  }
});
```

> ⚠️ 구버전 컬렉션(`allowed_users`, `edoc_users`, `access_requests`, `edoc_requests`)은
> 더 이상 참조하지 않음 (2026-06-26 제거 완료)

---

## 비밀번호 변경 (_pw 동기화)

```
[신규 계정 — _pw 있음]
  Firestore _pw 읽기 → atob 디코딩 → Secondary App signIn
  → updatePassword → _pw 갱신

[기존 계정 — _pw 없음, 최초 1회]
  "현재 비밀번호" 입력란 자동 표시 → 관리자 수동 입력
  → 위와 동일 흐름 + _pw 신규 저장 → 이후 자동화

[직원 본인 변경]
  updatePassword + _pw 동기화 (saveMyProfile)
```

---

## 부서·직급 체계

**부서 (optgroup)**
```
사업본부     → 현장관리팀 / 인력배치팀
경영지원본부  → 경영총무팀 / 영업기획팀
```

**직급**: 대표 / 부사장 / 차장 / 과장 / 대리 / 사원

---

## workers ↔ portal_users 연동 구조 (2026-06-27 개정)

### 마스터: workers (근로자 명부)

```
workers (마스터)
  └→ [역방향] portal_users 동기화
        트리거: hr 앱 명부 수정 저장 시
        동기화 필드: name · rank · dept · empNo
  └→ [읽기] 각 계약서
        함수: await window.getWorkerData(workerId)
        필드: jumin · phone · address · bankAccount · hireDate · job · empType · signData
  └→ [읽기] portal 직원 상세
        조회: workers where portalUid == uid
        표시: phone · jumin(마스킹) · address · bankAccount · hireDate · job (읽기 전용)
  └→ [읽기] 전자결재
        필드: signData (개인 서명)
```

### 필드 소유권

| 필드 | 소유 | 수정 위치 |
|------|------|---------|
| name, rank, dept, empNo | 공유 | hr 명부 수정 → portal 역방향 동기화 |
| jumin, address, bankAccount, hireDate, job, empType | workers 전용 | hr 앱 명부만 |
| phone | workers 전용 | hr 앱 명부 (portal 표시는 읽기 전용) |
| signData | workers 전용 | hr 앱 명부 서명 패드 |
| email, perms, admin, status, _pw | portal_users 전용 | portal 관리 |

### portal 직원 상세 표시 (2026-06-27 추가)

```js
// openEmpDetail(uid) — async
const wq = await getDocs(query(collection(db,'workers'), where('portalUid','==',uid)));
// workers 데이터를 읽기 전용으로 직원 상세 패널에 표시
// 주민번호는 앞 6자리 + ******* 마스킹
```

### 기존 미연동 계정 처리

- Portal 관리 목록 → `portalUid` 없는 계정 → "명부미연동" 배지
- "근무자 연동" 버튼 → `syncWorker(uid)` → workers 문서 생성 + portalUid 연결
- 이후 hr 앱 명부에서 jumin·phone 등 상세 정보 직접 입력
