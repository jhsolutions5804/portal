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
  signData:    string,    // 개인 서명 base64 (전자결재 연동용)
  registeredAt: string    // ISO 문자열
}
```

**workerId 형식**: `{이름}_{주민번호 13자리}` (예: `홍길동_9001011234567`)
> portal에서 자동 생성된 경우: `{이름}_portal_{uid 앞 6자리}`

---

## 연동 방향 (마스터 정책)

```
workers (근로자 명부) = 마스터
  └→ portal_users 역방향 동기화
        공유 필드: name · rank · dept · empNo
  └→ 각 계약서 (getWorkerData 호출)
        연동 필드: jumin · phone · address · bankAccount · hireDate · job · empType
  └→ 전자결재 (signData 로드)
        연동 필드: signData (개인 서명)
```

> portal 직원 상세에서 `portalUid`로 `workers` 조회 → 주민번호(마스킹)·주소·계좌·입사일 표시

---

## 화면 레이아웃 (v3, 2026-06-27)

- 탭 진입 즉시 근로자 명단 **테이블 직접 표시**
- 우측 상단 `➕ 신규 등록` 버튼 독립 배치
- `max-width: 1100px` PC 테이블
- 컬럼: 사원번호 · 이름 · 소속 · 직급 · 구분 · 생년월일 · 휴대폰 · 근로계약 · 연봉계약 · 포털 연동 · 삭제

### 포털 연동 표시
- 🔗 초록: `portalUid` 있음
- `미연동` 회색: 포털 계정 미연결 (명부는 정상 사용 가능)

---

## 주요 기능

### 수정 (이름 클릭 → 상세 모달)
- 전 필드 수정 가능: 이름·주민번호·휴대폰·주소·계좌·담당업무·소속·직급·구분·입사일
- 저장 시 `portalUid` 있으면 `portal_users` 역방향 동기화 (name·rank·dept)
- 사원번호: 목록에서 클릭 → 인라인 수정 → 저장 시 portal_users.empNo도 동기화

### 삭제
- 🗑 버튼 → confirm → `deleteDoc`
- 계약서 데이터(labor_contracts 등)는 유지

### 신규 등록
- 포털 가입자 드롭다운에서 선택 → 이름·직급·부서 자동 채움 + `portalUid` 저장
- 저장 시 사원번호 자동 부여 → `portal_users.empNo` 역방향 동기화
- 포털 미연동 근로자는 "직접 입력" 선택 후 수동 입력

---

## 개인 서명 (signData)

- 상세 모달 하단 **서명 패드** (canvas)
- 마우스·터치 모두 지원
- 저장 → `workers.signData` (base64 PNG)
- **전자결재(edoc)에서 `getWorkerData(workerId)` 호출 시 함께 로드됨**

---

## 계약서 연동 준비 (getWorkerData)

```js
// 전역 등록된 함수 — 각 계약서에서 호출
const w = await window.getWorkerData(workerId);
// 반환: { name, jumin, phone, address, dept, rank, job, empType,
//         hireDate, bankAccount, empNo, portalUid, signData }
```

사용 예정 위치: 근로계약서·연봉계약서·급여명세서·전자결재 (탭별 개별 연동 예정)

---

## 사번 자동 부여 규칙

```
empNo = 가입연도 2자리 + 해당 연도 순번 3자리
예) 2026년 첫 번째 → '26001'
```

---

## CRUD 주요 함수

| 함수 | 역할 |
|------|------|
| `renderRosterMain()` | 목록 테이블 렌더 (탭 진입 시 바로 표시) |
| `renderRosterRegister()` | 신규 등록 폼 |
| `rosterRegPortalSelect(uid)` | 드롭다운 선택 → 폼 자동 채움 |
| `rosterSave()` | workers 저장 + portal_users 역방향 동기화 |
| `rosterDetail(id)` | 상세/수정 모달 |
| `rosterDetailSave(id)` | 수정 저장 + portal_users 역방향 동기화 |
| `rosterDelete(id, name)` | 삭제 |
| `rosterEmpNoEdit/Save/Cancel(id)` | 사원번호 인라인 수정 |
| `rosterOpenSignPad(id)` | 서명 패드 오픈 |
| `rosterSignSave()` | 서명 canvas → base64 저장 |
| `window.getWorkerData(workerId)` | 계약서·전자결재 연동용 전역 함수 |
| `renderRosterList()` | renderRosterMain() 으로 리다이렉트 |
