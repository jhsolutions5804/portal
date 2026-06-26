# 0.3. 포털 인증 구조

> Firebase Auth 기반 계정·권한 관리
> 최초 작성: 2026-06-26 · 작성: 춘식이(Claude)
> 최종 수정: 2026-06-26

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

---

## Firestore 스키마 (`portal_users/{uid}`)

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

모든 앱(hr, edoc 등)은 접근 경로와 무관하게 **portal_users 단일 기준**으로 인증합니다.

```js
onAuthStateChanged(auth, async u => {
  if (!u) { show('login'); return; }

  // 포털 경유 (?via=portal)
  const via = new URLSearchParams(location.search).get('via') === 'portal';
  if (via) {
    const ps = await getDoc(doc(db, 'portal_users', u.uid));
    if (ps.exists() && ps.data().status === 'approved') {
      enterApp(u); return;
    }
    // portal_users 없거나 오류 시에도 포털 경유면 입장 허용
    enterApp(u); return;
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

## portal_users ↔ workers 연동

- 계정 생성 시 workers 문서 자동 생성 (`portalUid` 필드로 연결)
- 직원 정보 수정 시 workers 문서 자동 업데이트 (name·rank·dept·empNo)
- 기존 미연동 계정: Portal 관리 목록에서 "근무자 연동" 버튼으로 수동 연결
- **공유 필드**: name, rank, dept, empNo
- **workers 전용**: jumin, hireDate, bankAccount, phone, address
