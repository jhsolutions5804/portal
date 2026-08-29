# 3.1. 전자결재 — 업무일지 · 연차신청서 (+ 결재 공통 구조)

> Firestore 컬렉션: `edoc_daily`, `edoc_leave`
> 최초 작성: 2026-07-01 · 최종 개정: 2026-08-29 (r2 · 업무일지 권한오류 수정, 연차신청서 전면 개편) -20 (r1 · 업무일지 임시저장/반려 상태 수정 기능) · 작성: 춘식이(Claude)

---

## 결재 공통 구조 (approvalLine)

모든 전자결재 문서는 `approvalLine` 배열로 결재 흐름을 관리한다.

```js
approvalLine: [
  { role, uid, name, rank, status }
]
```

| role | 의미 |
|------|------|
| 작성 | 기안자 (본인) |
| 결재 / 결재1 / 결재2 | 결재자 |
| 수신 / 회람 | 통보·참조 대상 |

**문서 status 흐름:**
```
draft(임시저장) → pending(상신) → reviewing → approved(승인) / rejected(반려) → posted(게시)
```
- 결재 처리: `processApproval` 계열 — 현재 차례(uid 일치 + 그 단계 pending)인 사람만 승인/반려
- 결재함 "결재대기"는 approvalLine에 내 uid가 있고 현재 내 차례인 문서

---

## 업무일지 (edoc_daily)

### 스키마
```js
edoc_daily/{auto-id}:
{
  dtype:        'daily',
  status:       'draft'|'pending'|...,
  title:        string,
  date:         string,        // 작성일
  pjtId, pjtCode, pjtName,     // 연결 프로젝트(선택)
  todayWork:    string,        // 오늘 진행 업무 (필수, 상신 시)
  tomorrowWork: string,        // 내일 예정
  issue:        string,        // 이슈·특이사항
  authorUid, authorEmail, authorName, authorDept, authorRank,
  approvalLine: [...],         // 작성 / 결재(김종화) / 수신(송지훈) 고정
  createdAt:    serverTimestamp,   // 최초 등록 시에만 기록 (수정 시 유지)
  updatedAt:    serverTimestamp    // 수정 저장 시에만 기록 (신규 등록 시 없음)
}
```

### 작성 (`renderDailyWrite` → `dailySave`)
- 제목·오늘 업무 필수 (상신 시)
- 결재 라인 고정: 결재=김종화(부사장), 수신=송지훈(대표)
- 💾 임시저장(draft) / 📨 상신(pending)

### 수정 (임시저장/반려 상태, r1 — 2026-07-20)
- `renderDailyDetail`에서 작성자 본인 + `status==='draft'` 또는 `'rejected'`일 때 "✏️ 수정" 버튼 노출 (`canEdit`)
- 버튼 클릭 시 `renderDailyWrite(d)`로 기존 문서 전체를 넘겨 수정모드 진입 — 제목·일자·프로젝트·작성자정보·업무내용이 모두 미리 채워짐
- 수정모드에서는 화면 상단에 "임시저장 상태 수정 중" 배지 표시, 뒤로가기 시 상세화면으로 복귀
- 저장 시(`dailySave`) `window._dailyEditId`가 설정돼 있으면 신규 등록(`addDoc`) 대신 기존 문서에 `setDoc(..., {merge:true})`로 덮어씀 — 문서 중복 생성 없음
- 최초 `createdAt`은 보존하고, 수정 시에는 `updatedAt`만 추가로 기록
- 회수(`docRecall`) → 상태가 `draft`로 전환된 문서를 이 경로로 열어 수정 후 재상신 가능
- 신규 작성(`renderDailyWrite()`, 인자 없음)은 기존과 동일하게 동작 (하위호환)

### 열람 권한 (N6-1)
- `portal_users/{uid}.dailyViewTargets` 기반 (→ 3.0 문서 참조)
- 관리자 전체 / 일반은 본인 글 + 열람 허용된 사람 글

---

## 연차신청서 (edoc_leave)

### 스키마
```js
edoc_leave/{auto-id}:
{
  dtype:      'leave',
  status:     'draft'|'pending'|...,
  title:      string,
  leaveType:  string,          // 연차/반차/병가 등
  startDate, endDate:  string,
  days:       number,          // 사용 일수
  reason:     string,          // 사유 (필수)
  contact:    string,          // 비상 연락처
  deputyUid, deputyName,       // 업무 대행자 → approvalLine 회람
  authorUid, authorName, authorRank, authorDept,
  approvalLine: [...],
  createdAt:  serverTimestamp
}
```

### 작성 (`renderLeaveWrite` → `leaveSave`)
- 결재 라인: 작성 → **결재1**(선택) → **결재2**(김종화 고정, `jh.kim@jhsol.kr`) → 회람(대행자, 있을 때)
- 상신 시 결재1 필수
- 작성 함수가 문서류(`renderDocWrite`)와 별도 → `renderDocList`에서 leave만 `renderLeaveWrite` 분기

### 연차 현황 박스
- 로그인 계정의 부여/사용/잔여 일수 카드 표시


---

## 업무일지 권한 오류 수정 (r2, 2026-08-29)

### 증상
사원 계정에서 "업무일지" 탭 목록 조회 시 `Missing or insufficient permissions` 오류.

### 원인
`renderDailyList`가 다른 문서함(연차·구매·지출)과 달리 `edoc_daily` 컬렉션을 무필터로 통째로 조회한 뒤 브라우저에서 `dailyViewTargets`(구방식) 기준으로 걸러내는 옛날 구조였음. Firestore는 쿼리 결과 중 규칙(`canViewEdocDoc`)을 통과 못 하는 문서가 하나라도 섞여 있으면 요청 전체를 거부하는데, 관리자가 아닌 계정은 남이 쓴 비공개 글이 걸려서 통째로 막혔음. 저장 시 규칙이 요구하는 `viewerUids` 필드도 채우지 않고 있었음.

### 수정
1. 저장 시(`dailySave`) 작성자 본인의 `dailyViewTargets`(내 글 열람 허용 대상자, 본인 `portal_users` 문서에서 단일 get으로 안전 조회)를 `viewerUids`로 함께 저장.
2. 목록 조회를 다른 문서함들이 이미 쓰던 표준 함수 `fetchEdocDocs('daily')`로 교체 — 작성자/결재라인(viewerUids)/게시(posted)/관리자 네 갈래 분리쿼리라 규칙과 정확히 맞음.

⚠️ 잔여 한계: 결재자(김종화 부사장·송지훈 대표)가 관리자 계정이 아니면, 사원이 쓴 업무일지를 목록에서 직접 열람 못 할 수 있음 — `portal_users`의 타인 문서 읽기가 규칙상 막혀 있어 사원이 저장 시 결재자 UID를 `viewerUids`에 못 넣기 때문. 결재자가 admin이면 문제 없음(확인됨).

---

## 연차신청서 개편 (r2, 2026-08-29)

### 레이아웃 (`renderLeaveMain`)
좌-연차달력 / 우상-내 연차정보(부여·사용·잔여) / 우하-내 연차신청 리스트. 3단 구조에서 좌/우 2단으로 재편.

### 전 직원 캘린더 공개
캘린더는 **게시(posted, 관리자 확정)된 연차 전체**를 보여줌 — 승인만 되고 아직 게시 안 된 건 본인 것만, 게시된 건 전 직원 공개. `fetchEdocDocs('leave')`가 이미 "내 것+viewerUids+posted(+관리자는 전체)"를 반환하므로 별도 규칙 변경 없이 구현. 날짜에 마우스를 올리면 그 날 연차인 사람 이름·휴가종류 툴팁, 같은 날 여러 명 겹치면 `+N` 뱃지.

### 휴가 종류 (근로기준법·남녀고용평등법 기준 법정휴가로 정비)
```
연차(유급) · 반차-오전(유급) · 반차-오후(유급)
생리휴가(무급) · 출산전후휴가(유급) · 배우자출산휴가(유급) · 유산·사산휴가(유급)
육아휴직(무급) · 가족돌봄휴가(무급)
병가(유급) · 예비군/민방위(유급)
```
`DOC_CONFIG.leave.fields`의 `leaveType` 옵션 한 곳만 고치면 작성 폼에 자동 반영되도록 통일.

**주휴수당 개근 판정과 연동**: 결근 판정 시 승인된 휴가(유급·무급 불문)로 커버된 날은 결근으로 안 봄. 유급휴가만 근무시간에 반영(1일=8h, 반차=4h) — 상세: `2_8_hr_worktime.md`.

---

## 타임존 버그 수정 (2026-08-29)

`edocMonthlyStandardHours`에서 날짜를 `toISOString().slice(0,10)`으로 만들던 부분을 로컬 연/월/일 직접 조합 방식으로 수정. 상세 원인은 `2_8_hr_worktime.md` 참고.
