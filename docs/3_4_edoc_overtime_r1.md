# 3.4. 전자결재 — 초과근로 결재 (r6)

> Firestore 컬렉션: `edoc_overtime`, `overtime`, `annual_contracts/{workerId}/contracts`, `workers`
> 최초 작성: 2026-07-06 · 최종 수정: 2026-07-26(r6, 목록 노출 로직을 canView 표준 패턴으로 재수정) · 작성: 춘식이(Claude) · 릴리스: v2.1.0 → v2.1.1 → v2.6.2 → v2.6.4 → v2.6.7

---

## 개요

전자결재(`portal/edoc/index.html`)에 **초과근로 결재** 문서 타입을 추가했다. 근로자를 선택하면 통상임금을 자동 조회해 수당을 계산하고, 승인되면 인사 `overtime` 컬렉션에 자동 등록된다. (모바일은 `8_1_mobile_edoc` 참조)

---

## Firestore 스키마 — `edoc_overtime/{auto-id}`

```js
{
  dtype: 'overtime', status: 'pending',
  date, name, rank, workerId,
  hours,                 // 초과근로 시간
  rate,                  // 통상임금(원/h)
  amount,                // 수당 = round(rate × hours)
  reason,                // 사유 (선택 입력, 2026-07-21 추가)
  yearMonth,             // date.slice(0,7)
  authorUid, authorName, authorDept, authorRank,
  approvalLine: [작성, 결재(김종화 차장), 회람(김민서 대리)],
  linkedToOvertime: false,  // 인사 자동연동 중복방지 플래그
  createdAt: serverTimestamp,
}
```

---

## 통상임금 자동 계산

인사와 **동일 로직**을 이식(`otCalcAnnualSalary`, `otGetWage`, `otLoadWorkers`):

- 연봉계약서 최신 1건 조회: `annual_contracts/{workerId}/contracts` (orderBy contractDate desc, limit 1)
- `calcAnnualSalary(hourly, empType)`:
  - office: basic=h·8·5·4.345, fixedOt=h·12·4.345, fixedNight=0, weekly=h·8·4.345
  - field: basic=h·8·5·4.345, fixedOt=0, fixedNight=h·0.5·8·5·4.345, weekly=h·8·4.345
- **통상임금 rate = round((basic+fixedOt+fixedNight+weekly) / 209)**
- **수당 amount = round(rate × hours)**
- ⚠️ 연봉계약서가 없는 근로자(예: 임원)는 rate=0 → 수당 0 표시.

---

## 결재선 (고정)

```
작성(본인) → 결재: 김종화 차장 → 회람: 김민서 대리   (게시 단계 없음)
```

---

## 승인 시 인사 자동 연동 (핵심)

`docApprove`의 자동연동 체인에 추가:

```js
else if (newStatus === 'approved' && dtype === 'overtime' && !rawData.linkedToOvertime) {
  await addDoc(collection(db, 'overtime'), {
    date, name, rank, workerId, hours, amount, rate,
    reason: rawData.reason||'',
    yearMonth: date.slice(0,7), savedAt: serverTimestamp()
  });
  await setDoc(doc(db, 'edoc_overtime', docId), { linkedToOvertime: true }, { merge:true });
}
```

- 결재자(김종화)가 승인 → 다음 결재자 없음 → 문서 `approved` → 훅 발동 → 인사 `overtime`에 기록.
- `linkedToOvertime` 플래그로 재승인 시 **중복 등록 방지**.

### 🎯 진짜 근본 원인 규명 및 수정 (2026-07-26)

2026-07-24 self-heal(자동 재동기화)을 추가했음에도 정다애·이한영 건이 계속 인사에 반영되지 않아, 진단 페이지(`debug/overtime_check.html`, 읽기 전용)를 만들어 실제 Firestore 데이터를 직접 확인함. **`edoc_overtime` 문서 4건이 모두 `status: 'pending'`(승인 안 됨) 상태로 남아있었음** — self-heal은 `status==='approved'`인 문서만 다루므로 애초에 대상이 아니었던 것. 즉 self-heal은 정상 동작했지만, **승인 자체가 Firestore에 반영되지 않는 더 근본적인 버그**가 있었음.

**원인**: `docDetail()`의 승인 버튼 노출 조건(`canApprove`)에는 관리자 예외가 있었음:
```js
const canApprove = isMyTurn || (_isAdmin && (d.status==='pending'||d.status==='reviewing'));
```
하지만 실제 처리 로직인 `docApprove()` 내부의 `isMyStep()`에는 이 관리자 예외가 없어서, 결재라인에 지정된 사람(예: 김종화) 본인이 아닌 **관리자 계정(대표님)이 대신 승인**하면 "내 결재 차례"를 하나도 찾지 못해 `approvalLine`이 전혀 갱신되지 않았고, 그 상태로 저장을 시도하다 실패한 것으로 추정됨(정확한 실패 지점은 Firestore 보안 규칙 검증 로그가 없어 100% 특정은 못했으나, 증상과 코드 분석이 정확히 일치함).

**수정** — `docApprove()`의 `isMyStep` 로직을 순번 기반 단일 단계 타겟팅으로 재작성:
1. 1순위: `uid`/이름이 정확히 일치하는, 순번상 차례가 된 단계
2. 2순위: 그래도 없으면 **관리자는 순번상 차례가 된 단계를 대신 승인 가능**
3. `targetIdx`를 단 하나만 확정해서, 다단계 결재라인(결재1→결재2 등)에서 관리자가 대신 승인해도 **여러 단계가 한 번에 승인 처리되는 사고를 방지**함 (`origLine.indexOf(s)===targetIdx`로 정확히 하나만 매칭)

**진단 도구**: `debug/overtime_check.html` — ID/PW 로그인 후 `edoc_overtime`·`overtime` 컬렉션 전체를 표로 보여주는 읽기 전용 페이지. Firestore를 Claude 환경에서 직접 조회할 수 없고, 대표님이 비개발자라 로컬 스크립트 실행도 어려운 상황에서 "링크만 열면 바로 확인 가능"하도록 만듦. 최초엔 Google 로그인으로 잘못 만들어 한 번 수정함(포털은 ID/PW 로그인 방식).

### ⚠️ 자동연동 실패 사례 및 self-heal 대응 (2026-07-24)

2026-07-23 즈음 승인한 초과근로 2건(이한영·정다애)이 인사 `overtime` 컬렉션에 반영되지 않는 문제가 발생. Firestore를 직접 조회할 수 없는 환경 제약으로 근본 원인(권한 문제/일시적 오류 등)은 특정하지 못했으나, **원인과 무관하게 항상 자가복구되도록** `hr/index.html`에 안전장치를 추가함.

- `hr/index.html`의 `window.otSyncFromEdoc()`: 인사 → 초과근로 탭 진입(`renderOvertimeMain`) 시마다 `edoc_overtime`에서 `status==='approved' && !linkedToOvertime`인 문서를 찾아 자동으로 `overtime`에 추가 + `linkedToOvertime:true` 마킹
- 즉, `docApprove()`의 즉시연동이 어떤 이유로든 실패해도, 인사 앱에서 초과근로 탭을 한 번만 열면 자동으로 따라잡는다 (idempotent, 몇 번을 열어도 중복 없음)
- 관련 진단 스크립트(`scripts/check_overtime_link.py`, Firestore Admin SDK 직접 조회용)도 함께 추가했으나, self-heal 도입 후에는 필수 사용처는 아님 — 향후 유사 연동 이슈 원인 규명이 필요할 때 참고용으로 남겨둠

### 🐛 별개로 발견된 이슈 (미해결, 2026-07-23 발견)

`결재함`(`renderApproveBox` → `loadApproveData()`)의 조회 대상 `DOC_TYPES` 배열에 `'overtime'`이 누락되어 있음. `TYPE_LABEL`에는 `overtime:'초과근로'`가 이미 등록되어 있어 원래는 결재함에도 노출될 의도였던 것으로 보이나, 실제로는 `edoc_overtime` 컬렉션을 조회하지 않아 결재함에 절대 나타나지 않는다. 현재는 "전자결재 → 초과근로" 전용 탭에서만 승인 가능(2026-07-23부터는 본인이 상신한 것만 보임 — r3 참조). 결재자가 타인이 상신한 초과근로를 승인하려면 여전히 이 전용 탭에 직접 들어가야 하며, 결재함에서는 확인 불가능한 상태. 다음 세션에서 `DOC_TYPES`에 `'overtime'` 추가 여부 결정 필요.

---

## UI

- `EDOC_TABS`·`DOC_CONFIG`·사이드바·탭바에 `overtime` 등록. `DOC_CONFIG.overtime.fields`: 근로자·일자·시간·통상임금·수당·**사유**(2026-07-21 추가).
- **초과근로 작성**(`renderOvertimeWrite`) 폼: 일자 → 근로자 선택 시 통상임금 자동 표시 → 시간 입력 시 수당 자동 → **사유**(선택, 텍스트영역).
- **임베드 대응**: `.portal-embed`에서 탭바/사이드바가 숨겨지므로, **전자결재 홈에 `goTab('overtime')` 진입 버튼**을 별도 배치.
- 목록(`renderOvertimeMain`): 2026-07-23엔 "본인 작성분만" 필터를 걸었으나, 이 때문에 관리자/결재자가 **본인이 작성하지 않은 결재 대상 문서를 볼 수 없어 결재가 아예 불가능해지는 회귀**가 발생함(2026-07-26 발견). `renderDocList`와 동일한 `canView` 표준 패턴으로 재수정: 관리자(전체) / 본인 작성 / 결재라인에 uid·이름으로 지정된 건만 노출. 카드 클릭 → `docDetail(d, 'overtime')`로 상세+승인/반려. 뒤로가기는 `renderOvertimeMain`. 상세 화면에 사유 표시.
  - ⚠️ 다른 사람이 상신한 초과근로를 결재/확인해야 하는 경우는 이 목록이 아니라 **결재함(`renderApproveBox`, `goTab('approve')`)**에서 처리한다. 이 목록은 어디까지나 "내가 상신한 것" 트래킹용.
- 작성(`renderOvertimeWrite`): 날짜 → 근로자 선택 시 통상임금 자동 표시 → 시간 입력 시 수당 자동.

---

## 관련 커밋 (2026-07-06)
과제⑤ 통합(초과근로 탭·통상임금·자동연동) → 홈 진입버튼 추가(임베드 대응) → 카드 클릭 상세(docDetail 연결) → 본섭 배포(d04fa60).

## 관련 커밋 (2026-07-21)
초과근로 상신 폼·상세보기·인사 자동연동에 **사유(reason)** 필드 추가 (선택 입력). `hr/2_4_hr_overtime` 문서 동시 갱신.
