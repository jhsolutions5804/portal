# 6. Portal 관리

> 관리자(대표) 전용 메뉴 · `portal/index.html`
> 최초 작성: 2026-06-26 · 최종 수정: 2026-06-27 · 작성: 춘식이(Claude)

---

## 접근 조건

- `portal_users.admin === true` 인 계정만 사이드바에 표시
- `jh.kim@jhsol.kr` = 자동 관리자 등록

---

## 직원 계정 생성

```
이름 + 직급(드롭박스) + 부서(optgroup, 선택사항)
  + 아이디(id@jhsol.kr) + 비밀번호(6자 이상)
→ createUserWithEmailAndPassword(auth2, email, pw)   // Secondary App
→ setDoc(portal_users/{uid}, {
    ..., status:'approved', admin:false, perms 전부 false,
    empNo: 자동부여, _pw: btoa(encodeURIComponent(pw))
  })
→ workers/{workerId} 자동 생성 (portalUid로 연결)
    생성 필드: name, rank, dept, empNo, portalUid
    미입력 필드: jumin, phone, address, bankAccount, hireDate, job, empType, signData
    → hr 앱 근로자 명부에서 별도 입력 필요
→ signOut(auth2)  // 관리자 세션 유지
```

---

## 직원 상세 — 명부 정보 표시 (2026-06-27 추가)

직원 상세 화면(`emp-detail`)에서 연동된 `workers` 문서를 자동 로드하여 읽기 전용으로 표시:

```
portal 직원 상세 열기
  → workers where portalUid == uid 조회
  → 아래 필드를 읽기 전용 패널로 표시 (hr 앱에서 수정 안내)
      · 주민번호 (앞 6자리만, 뒷자리 ******* 마스킹)
      · 주소
      · 계좌번호
      · 입사일
      · 담당업무
  → 전화번호: workers.phone 우선, 없으면 portal_users.phone 폴백
```

> workers 문서가 없는 계정은 명부 정보 섹션 미표시 (오류 없이 처리)

---

## 직원 정보 수정 (`saveEmpDetail`)

```
portal 직원 상세에서 수정 저장 시
  → portal_users 업데이트: empNo · name · rank · dept · phone
  → workers 역방향 동기화: name · rank · dept · empNo
    (workers가 마스터이므로 최소 공유 필드만 동기화)
```

> jumin·address·bankAccount 등 workers 전용 필드는 **hr 앱 명부에서만 수정**

---

## 직원 비밀번호 변경

```
[_pw 있음 — 신규 계정]
  _pw 읽기 → atob 디코딩 → Secondary App signIn
  → updatePassword → _pw 갱신

[_pw 없음 — 기존 계정, 최초 1회]
  "현재 비밀번호" 입력란 자동 표시
  → 관리자 수동 입력 후 처리
  → 이후 자동화
```

---

## 접근 권한 관리

```
portal_users (status=approved, admin=false) 목록
  → 칩 버튼으로 perms.{plan|hr|edoc|pjt} 토글
  → updateDoc(portal_users/{uid}, {'perms.key': bool})
```

---

## 기존 계정 근로자 연동

- Portal 관리 목록에서 `portalUid` 없는 계정 → "명부미연동" 배지
- "근무자 연동" 버튼 → `syncWorker(uid)` 호출
  - workers 문서 생성 (name·rank·dept·empNo·portalUid)
  - portal_users.empNo 동기화
- **연동 후** hr 앱 근로자 명부에서 jumin·phone 등 상세 정보 입력

---

## Secondary App 패턴

```js
// 관리자 세션(auth)에 영향 없이 타 계정 조작
const app2 = initApp2(firebaseConfig, 'pw-chg-' + Date.now());
const auth2 = getAuth(app2);
const cred = await signInWithEmailAndPassword(auth2, email, curPw);
await updatePassword(cred.user, newPw);
await signOut(auth2);
```
