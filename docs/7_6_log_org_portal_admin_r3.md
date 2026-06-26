# 7.6. 개발 로그 — 조직도

> 최초 작성: 2026-06-26 · 작성: 춘식이(Claude)

---

## 현재 상태

- 구현 예정
- 이력 없음

---

# 7.7. 개발 로그 — Portal 관리

> `portal/index.html` 내 Portal 관리 기능
> 최초 작성: 2026-06-26 · 최종 수정: 2026-06-27 · 작성: 춘식이(Claude)

---

## 커밋 이력

| SHA | 날짜 | 내용 |
|-----|------|------|
| `3dfbd4bc` | 2026-06-25 | Portal 관리 신설 — 직원 ID 생성·접근권한, 가입 승인 삭제 |
| `05308797` | 2026-06-25 | 계정 생성 부서·직급 드롭박스 추가 |
| `57473bf4` | 2026-06-25 | 직원 비밀번호 변경 UI (Secondary App 방식) |
| `6eee2bfa` | 2026-06-25 | _pw 자동 동기화 + 기존 계정 최초 1회 입력 처리 |
| `843f3a40` | 2026-06-25 | 기존 계정 최초 1회 현재PW 입력란 조건부 표시 |
| `2c934054` | 2026-06-26 | A4+B6 portal↔workers 연동 완성 |
| `0ff52f10` | 2026-06-27 | 직원 상세 workers 명부 정보 로드 (workers→portal 방향) — 로그 기록만, 실제 미반영 |
| `bdb7ae66` | 2026-06-27 | fix: openEmpDetail async화 + workers 명부 정보 로드 실반영 |

---

## 주요 변경 상세

### 2026-06-25: 비밀번호 변경 완성
- Secondary App으로 signIn → updatePassword → _pw 갱신
- 기존 계정: 최초 1회 현재 비밀번호 수동 입력

### 2026-06-26: portal ↔ workers 연동 (A4+B6)

**신규 계정 생성 시**
- workers 컬렉션에 자동으로 근로자 명부 문서 생성 (`portalUid` 필드로 영구 연결)
- empNo 자동 부여 (가입연도2자리 + 연도순번3자리)
- 생성 필드: name·rank·dept·empNo·portalUid
- 미입력 필드 → hr 앱에서 직접 입력: jumin·phone·address·bankAccount·hireDate·job·empType·signData

**직원 정보 수정 시 (`saveEmpDetail`)**
- portal_users 업데이트 후 workers 공유 필드 역방향 동기화 (name·rank·dept·empNo)

**기존 미연동 계정**
- "명부미연동" 배지 + "근무자 연동" 버튼
- `syncWorker(uid)` 호출로 workers 문서 생성

### 2026-06-27: workers 명부 정보 로드 실반영 (`bdb7ae66`)

**배경**
`0ff52f10` 커밋에서 `portal_index_v2.html`로 수정했으나, 로그와 실제 배포 파일 비교 시 누락 항목 확인:
- openEmpDetail이 동기 함수 그대로
- 📋 근로자 명부 정보 섹션 미표시
- workers.phone 폴백 미적용
- onblur 속성 중복

**실반영 내용**

```js
// openEmpDetail → async function으로 변경
async function openEmpDetail(uid) {
  ...
  // workers portalUid 쿼리로 명부 데이터 로드
  let workerData = { phone:'', jumin:'', address:'', bankAccount:'', hireDate:'', job:'', empType:'' };
  try {
    const wq = await getDocs(query(collection(db,'workers'), where('portalUid','==',uid)));
    if (!wq.empty) { workerData = { ...wq.docs[0].data() }; }
  } catch(we) { console.warn('workers 로드 실패:', we); }
  ...
}
```

- 전화번호: `workerData.phone||u.phone` (workers 우선, 없으면 portal_users 폴백)
- 직원 상세 패널에 📋 근로자 명부 정보 섹션 추가 (읽기 전용):
  - 주민번호: 앞 6자리 + `*******` 마스킹
  - 주소·계좌·입사일·담당업무
  - "(hr 앱에서 수정)" 안내 문구
- workers 없는 계정 → 섹션 미표시, 오류 없이 처리
- `onblur` 속성 중복 제거

---

## 이슈 & 해결

| 이슈 | 해결 |
|------|------|
| 직원 상세 `ed-dept`에 guest 부서 누락 | `deptOpts`에 guest 옵션 추가 |
| 기존 계정 _pw 없음 → 비밀번호 변경 실패 | 최초 1회 현재 비밀번호 수동 입력 후 자동화 |
| 0ff52f10 커밋 내용이 실제 portal에 미반영 | 로그 vs 실제 파일 비교 후 bdb7ae66으로 실반영 |
| workers 없는 계정 openEmpDetail 오류 | try-catch workerData 기본값 처리 |
