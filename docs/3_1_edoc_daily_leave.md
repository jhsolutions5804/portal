# 3.1. 전자결재 — 업무일지 · 연차신청서 (+ 결재 공통 구조)

> Firestore 컬렉션: `edoc_daily`, `edoc_leave`
> 최초 작성: 2026-07-01 · 작성: 춘식이(Claude)

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
  createdAt:    serverTimestamp
}
```

### 작성 (`renderDailyWrite` → `dailySave`)
- 제목·오늘 업무 필수 (상신 시)
- 결재 라인 고정: 결재=김종화(부사장), 수신=송지훈(대표)
- 💾 임시저장(draft) / 📨 상신(pending)

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
