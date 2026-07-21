# 3.4. 전자결재 — 초과근로 결재 (r2)

> Firestore 컬렉션: `edoc_overtime`, `overtime`, `annual_contracts/{workerId}/contracts`, `workers`
> 최초 작성: 2026-07-06 · 최종 수정: 2026-07-21(r2, 사유 필드 추가) · 작성: 춘식이(Claude) · 릴리스: v2.1.0 → v2.1.1

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

---

## UI

- `EDOC_TABS`·`DOC_CONFIG`·사이드바·탭바에 `overtime` 등록. `DOC_CONFIG.overtime.fields`: 근로자·일자·시간·통상임금·수당·**사유**(2026-07-21 추가).
- **초과근로 작성**(`renderOvertimeWrite`) 폼: 일자 → 근로자 선택 시 통상임금 자동 표시 → 시간 입력 시 수당 자동 → **사유**(선택, 텍스트영역).
- **임베드 대응**: `.portal-embed`에서 탭바/사이드바가 숨겨지므로, **전자결재 홈에 `goTab('overtime')` 진입 버튼**을 별도 배치.
- 목록(`renderOvertimeMain`): 카드 클릭 → `docDetail(d, 'overtime')`로 상세+승인/반려. 뒤로가기는 `renderOvertimeMain`. 상세 화면에 사유 표시.
- 작성(`renderOvertimeWrite`): 날짜 → 근로자 선택 시 통상임금 자동 표시 → 시간 입력 시 수당 자동.

---

## 관련 커밋 (2026-07-06)
과제⑤ 통합(초과근로 탭·통상임금·자동연동) → 홈 진입버튼 추가(임베드 대응) → 카드 클릭 상세(docDetail 연결) → 본섭 배포(d04fa60).

## 관련 커밋 (2026-07-21)
초과근로 상신 폼·상세보기·인사 자동연동에 **사유(reason)** 필드 추가 (선택 입력). `hr/2_4_hr_overtime` 문서 동시 갱신.
