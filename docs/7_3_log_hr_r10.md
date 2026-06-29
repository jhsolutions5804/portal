# HR 모듈 개발 로그 r10
> 최초 작성: 2026-06-29(r10) · 작성: 춘식이(Claude)

## 오늘(2026-06-29) 작업 커밋 이력

| SHA | 코드 | 내용 |
|-----|------|------|
| `d878cebf` | J3 | 연차현황 `_isAdmin` URL 파라미터 수신 코드 추가 |
| `d878cebf` | J4 | 퇴직금 드롭박스 `empNo` 기준 정렬 |
| `d878cebf` | J5 | 퇴직금 PC뷰 `rt-list-panel` 저장 내역 연동 (`rtLoadListPanel`) |
| `d878cebf` | J6 | HR 전체 여백 `max-width:1100px` 통일 (840px→1100px) |
| `a5b9497e` | K1 | 급여명세서 지급계·실지급액 `c.gross→c.totalPay`, `c.net→c.netPay` 수정 |
| `a5b9497e` | K2 | 전체 드롭박스 `empNo` 정렬 통일 (`getWorkersList` name 정렬 제거) |
| `f56b7b1e` | L2 | `rosterSave` 완료 후 `portal_users` 역방향 연동 |
| `f56b7b1e` | L3 | 근로자 명부 수정 모달 `oninput` `f.key` 런타임 참조 오류 수정 |
| `03e16c6f` | — | 근로자 명부 상세 모달 🔗 포털 계정 연동 버튼 추가 (`rosterLinkPortal`) |
| `e0d0004b` | — | `rosterLinkPortal` portal_users 직접 쓰기 → `postMessage` 위임으로 수정 |

---

## J3 — 연차현황 관리자 기능 (`d878cebf`)
### 원인
`portal/index.html`이 `&admin=1` 파라미터를 URL에 전달하지만 `hr/index.html`에서 수신 코드 없음 → `window._isAdmin` 항상 `undefined` → 연차 등록 버튼 미표시.

### 수정
```js
// showScreen() 내 추가 (URLSearchParams 처리 직후)
if (params.get('admin') === '1') window._isAdmin = true;
```

---

## J4 — 퇴직금 드롭박스 정렬 (`d878cebf`)
### 원인
`getWorkersList()`가 `empNo` 정렬 후 `name` 정렬로 덮어씀.

### 수정
`renderRetirePC()` / `renderRetireCalcMobile()` 각각 `_rtWorkers` 로드 직후:
```js
_rtWorkers.sort((a,b)=>(a.empNo||'zzz').localeCompare(b.empNo||'zzz'));
```

---

## J5 — 퇴직금 rt-list-panel 연동 (`d878cebf`)
### 원인
`rt-list-panel` 업데이트 함수 없음 → 저장 후 내역 조회 불가.

### 수정
`rtLoadListPanel(wid)` 신규 함수 추가:
- `severance/{wid}/records` 조회 → 퇴직일 최신순 렌더
- `retireCompute()` wid 확정 시 호출
- `retireSave()` 후 `renderRetireMain()` 대신 패널만 갱신

---

## K1 — 급여명세서 지급계·실지급액 (`a5b9497e`)
### 원인
`psCalcAll()` 반환값: `totalPay`, `netPay`
`renderPayslipPCRight()` 참조: `c.gross`, `c.net` → `undefined` → 항상 0원

### 수정
```js
// 수정 전
${won(c.gross)}  /  ${won(c.net)}
// 수정 후
${won(c.totalPay)}  /  ${won(c.netPay)}
```

---

## K2 — 전체 드롭박스 empNo 정렬 (`a5b9497e`)
### 수정 위치
| 위치 | 수정 내용 |
|------|---------|
| `getWorkersList()` | `name` 정렬 제거 → `empNo` 단일 정렬 (`zzz` 후치) |
| 급여명세서 PC select | `name rank` → `[empNo] name (rank)` 표시 |
| `otGetWorkerList()` | 빈 `empNo` → `zzz` 후치 통일 |
| 퇴직금 모바일 select | `empNo` 표시 추가 |

---

## L2 — rosterSave portal_users 역방향 연동 (`f56b7b1e` → `e0d0004b`)
### 동작
`rosterSave()` 완료 후 이름으로 `portal_users` 매칭:
- 1건 매칭: `workers.portalUid` + `portal_users.workerId/empNo` 상호 업데이트
- 0건/동명이인: 연동 생략

### 권한 이슈 해결
`hr`에서 `portal_users` 직접 `updateDoc` → `Missing or insufficient permissions`
→ `window.parent.postMessage({ source:'jh-hr', action:'linkWorkerToPortal' })` 로 portal에 위임
→ `portal/index.html`에 `message` 수신기 추가

---

## L3 — 근로자 명부 수정 모달 oninput 오류 (`f56b7b1e`)
### 원인
```js
// 문제: map() 내 f.key가 oninput 핸들러 런타임에 undefined
oninput="window._editRosterTarget['${f.key}']=(f.key==='phone'?...)"
//                                                ^^^^ 런타임 참조 오류
```
### 수정
```js
// f.key → '${f.key}' 로 빌드 시점에 치환
oninput="window._editRosterTarget['${f.key}']=(('${f.key}')==='phone'?...)"
```

---

## 포털 계정 연동 버튼 (`03e16c6f` → `e0d0004b`)
### 기능
근로자 명부 상세 모달 하단에 **🔗 포털 계정 연동** 버튼 추가.
- 미연동 상태: 연동 버튼 표시
- 연동 완료 상태: ✅ 포털 계정 연동됨 표시
- 동작: `rosterLinkPortal(workerId, workerName)` 호출 → `postMessage` 방식
