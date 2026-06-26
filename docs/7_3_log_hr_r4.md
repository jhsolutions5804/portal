# 7.3. 개발 로그 — 인사 앱

> `portal/hr/index.html` 변경 이력
> 최초 작성: 2026-06-26 · 최종 수정: 2026-06-27 · 작성: 춘식이(Claude)

---

## 커밋 이력

| SHA | 날짜 | 내용 |
|-----|------|------|
| *(초기)* | 2026-06-24 | 7개 탭: 홈·명부·근로계약·연봉계약·초과근로·급여·퇴직금 |
| *(Rev2)* | 2026-06-25 | 연차 현황 탭(8번) 추가 |
| `2cf3c6996b` | 2026-06-26 | Firebase config 원본 복원 |
| `668d253f` | 2026-06-27 | [D1] hr 내부 사이드바 완전 제거 |
| `6c236d60` | 2026-06-27 | [D2] 명부 PC 레이아웃 + portal_users 드롭다운 연동 |
| `755521e6` | 2026-06-27 | [D3] 명부 v3 — 수정/삭제 복구·서명패드·계약서연동·역방향동기화·2번항목제거 |

---

## D3 상세 (2026-06-27, `755521e6`)

### 1번 — 수정/삭제 복구
D2 배포 시 코드 교체 과정에서 누락된 함수들 복구:
- `rosterDetail(id)` — 이름 클릭 → 상세/수정 모달
- `rosterDetailSave(id)` — 모달 저장
- `rosterDelete(id, name)` — 삭제 confirm + deleteDoc
- `rosterEmpNoEdit/Save/Cancel(id)` — 사원번호 인라인 수정 (취소 버튼 추가)

### 2번 — 연동 버튼 제거
- 포털 열 `연동` 버튼 제거
- `rosterLinkPortal`, `rosterLinkPortalSave` 함수 완전 삭제
- `portalUid` 없는 경우 `미연동` 텍스트 표시만 유지

### 3번 — 연동 방향 역전 (workers → portal_users)
- `rosterDetailSave`: workers 수정 후 `portal_users` name·rank·dept 역방향 업데이트
- `rosterSave`: 신규 등록 후 empNo를 `portal_users`에 역방향 동기화
- `rosterEmpNoSave`: 사원번호 수정 후 `portal_users.empNo` 동기화

### 4번 — 계약서 연동 준비
```js
window.getWorkerData = async (workerId) => {
  // workers/{workerId} 문서 전체 반환
  // 반환: { name, jumin, phone, address, bankAccount, hireDate, job, empType, signData, ... }
};
```
계약서 탭에서 `await window.getWorkerData(workerId)` 호출로 언제든 연동 가능.

### 5번 — 개인 서명 등록
- 상세 모달 내 서명 패드 (canvas, 380×120px)
- 마우스·터치 이벤트 모두 지원
- `rosterSignSave()` → `workers.signData` base64 저장
- 기존 서명 있으면 미리보기 표시 + 지우기 버튼
- edoc에서 `getWorkerData` 호출 시 signData 함께 로드됨

---

## 7.1b. 개발 로그 — 포털 홈 (portal/index.html)

| SHA | 날짜 | 내용 |
|-----|------|------|
| `0ff52f10` | 2026-06-27 | feat: 직원 상세 workers 명부 정보 로드 (workers→portal 방향) |

### 변경 내용
- `openEmpDetail` → `async function`으로 변경
- 함수 진입 시 `workers` 컬렉션에서 `portalUid`로 조회
- 조회된 workerData를 직원 상세 패널에 읽기 전용으로 표시:
  - 주민번호 (앞 6자리만, 뒷자리 `*******` 마스킹)
  - 주소
  - 계좌번호
  - 입사일
  - 담당업무
- 전화번호: `workerData.phone` 우선, 없으면 `portal_users.phone` 폴백
- workers 없는 계정은 해당 섹션 미표시 (오류 없이 처리)
- 안내 문구: `(hr 앱에서 수정)` — 명부가 마스터임을 명시

---

## 이슈 & 해결

| 이슈 | 해결 |
|------|------|
| D2에서 rosterDetail 등 누락 | 코드 교체 범위 오류 → D3에서 전체 재교체 |
| rosterEmpNoCancel 없어 인라인 수정 취소 불가 | 취소 버튼 + 함수 추가 |
| 서명 canvas 터치 이벤트 스크롤 충돌 | `e.preventDefault()` + `touch-action:none` 적용 |
| portal_users 역방향 동기화 실패 시 전체 롤백 | try-catch 독립 처리 (명부 저장은 성공으로 처리) |
