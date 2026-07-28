# 3.3. 전자결재 — 퇴직원서 · 재직증명서 · 구매품의서 · 지출결의서

> Firestore 컬렉션: `edoc_resign`, `edoc_cert`, `edoc_purchase`, `edoc_expense`
> 최초 작성: 2026-07-01 · 최종 수정: 2026-07-24(r3) · 작성: 춘식이(Claude)

---

## 개요

4개 문서류는 **설정 기반(`DOC_CONFIG`)**으로 동작한다. 공통 함수(`renderDocWrite`/`docSave`/`renderDocList`)가 dtype별 설정만 바꿔 재사용된다. (연차 `leave`도 같은 틀이나 작성 함수만 별도)

---

## DOC_CONFIG 구조

```js
DOC_CONFIG[dtype] = {
  label:     string,            // 표시명
  icon:      string,            // 이모지
  approvers: [이름...],          // 고정 결재자
  cc:        [이름...],          // 회람 대상
  fields:    [                  // 입력 필드 정의
    { key, label, type, ph?, opts? }   // type: text|textarea|date|number|select|money|urls|items
  ]
}
```

### 문서별 설정

| dtype | 명칭 | 결재자 | 회람 | 주요 필드 |
|-------|------|--------|------|----------|
| `resign` | 퇴직원서 | 김종화·김영희·송지훈 | 김민서 | 퇴직예정일, 퇴직사유 |
| `cert` | 재직증명서 | 김종화 | — | 용도, 발급언어, 부수 |
| `purchase` | 구매품의서 | 김종화 | — | 공급업체, 목적, 필요일, **구매 품목(다중, 품목별 링크 포함)** |
| `expense` | 지출결의서 | 김종화 | — | 지출일, 구분, 금액, 거래처, 목적, 증빙, **구매 품목(다중, 품목별 링크 포함)** |

---

## 공통 스키마

```js
edoc_{dtype}/{auto-id}:
{
  title:        string,         // 자동 생성 (yyyymmdd 이름 문서명)
  dtype:        string,
  status:       'draft'|'pending'|...,
  authorUid, authorName, authorRank, authorDept,
  approvalLine: [...],          // buildFixedApprovalLine(dtype)
  createdAt:    serverTimestamp,
  // + DOC_CONFIG.fields의 각 key가 동적으로 저장됨 (f.key → data[f.key])
}
```

---

## 고정 결재라인 (buildFixedApprovalLine)

```
[작성(본인)]
 + approvers 각 이름 → findUserByName으로 uid 매칭
   (결재자 1명이면 role='결재', 여럿이면 '결재1','결재2'…)
 + cc 각 이름 → role='회람'
```

---

## 핵심 함수

| 함수 | 동작 |
|------|------|
| `renderDocMain(dtype)` → `renderDocList(dtype)` | 조회 테이블 (5탭 공용) |
| `renderDocWrite(dtype)` | 작성 폼 — DOC_CONFIG.fields 순회 렌더 |
| `docSave(dtype, status)` | 저장 — fields 값을 동적으로 수집해 `edoc_{dtype}`에 addDoc |
| `renderDocDetail` | 상세·결재 화면 |

---

## 레이아웃 (N6-3~6)

- 진입 시 바로 조회 테이블(`.ptable`), 우측 상단 🏠 홈 + ✏️ 작성 버튼
- 초기 로딩 문구 없음 → 데이터 오면 테이블 또는 "등록된 문서가 없습니다"
- 상세에서 뒤로가기는 직전 화면 복귀 (→ 3.0 N8/N9 참조)

---

## 문서 제목 자동 생성

```
yyyymmdd + 이름 + 문서명   (예: 20260701 정다애 지출결의서)
```

---

## 구매 품목 다중입력 (구매품의서·지출결의서 공용) — r3, 2026-07-24

두 문서 모두 `items` 필드(`type:'items'`, 선택)를 폼 **하단**에 배치. 품목명·수량·단가·링크를 한 행으로 묶어 여러 행 입력 가능(가로 배치).

- `+ 품목 추가` 버튼으로 행 무제한 추가(`addItemRow`), 각 행 우측 `−` 버튼으로 삭제
- 행 구성: 품목명(text) · 수량(number) · 단가(money, `fmtMoney` 실시간 콤마) · 링크(url, 품목별 개별 입력)
- 저장(`docSave`): `.item-row`를 순회해 `{name, qty, unitPrice, amount(=qty×unitPrice), link}` 객체 배열로 수집. 4개 값이 모두 빈 행은 저장 시 제외
- 표시(상세보기 `docDetail`, 인쇄 `printDocA4`): `fmtItemsTable()`이 품명·수량·단가·금액·링크 표 + 하단 합계 행으로 렌더링. 링크는 새 탭으로 열림
- 지출결의서는 기존 `amount`(총 지출 금액, 수기 입력) 필드는 그대로 유지 — `items`는 지출 내역의 구매 품목 상세/증빙 성격으로 추가된 것이며 amount를 자동 대체하지 않음

### 하위호환 (구조 변경 이전 문서)

`items` 도입 이전 구매품의서는 `item`(단일 텍스트)/`qty`/`unitPrice`/`refUrls`(URL 배열) 구조로 저장돼 있음. `getItemsForDisplay(d, dtype)`가 `d.items`가 없으면 위 레거시 필드로 1행짜리 품목(링크는 `refUrls[0]`)을 구성해 동일한 표로 보여준다 — **과거 문서 조회 시 화면이 비어 보이지 않도록 하는 읽기 전용 호환 처리**이며, 저장 로직에는 영향 없음.


---

## UI — 금액 입력 포맷 (r2, 2026-07-23)

구매품의서 단가(`unitPrice`)·지출결의서 금액(`amount`) 필드를 `DOC_CONFIG`에서 `type:'money'`로 신설. 렌더러는 텍스트+실시간 콤마(`fmtMoney`), `docSave`는 콤마 제거 후 숫자로 저장, 상세보기(`docDetail`)도 `Number(v).toLocaleString('ko-KR')+'원'` 형식으로 표시. 상세: `7_4b_log_edoc.md`


---

## v3.5 변경 요약 (2026-07-28) — 모바일 구매품의서·지출결의서 실연동

- 기존 모바일(`m/edoc.html`)은 구매품의서/지출결의서를 "준비 중" 스텁으로만 표시 → `edoc_purchase`/`edoc_expense` 컬렉션 실시간 구독으로 교체
- 목록·상세·작성(품목 다중입력: 품목명/수량/단가)·삭제·결재(승인/반려) 전부 지원. PC와 동일한 필드 스키마(vendor/purpose/dueDate/items, expDate/category/amount/vendor/purpose/receipt/items) 사용 → 상호 조회 가능
- 결재선: 결재 1단계(김종화 차장), PC의 `DOC_CONFIG.purchase/expense.approvers`와 동일
- 결재함(`renderApprove`)에 구매품의·지출결의·초과근로까지 함께 노출되도록 통합 (기존엔 업무일지·연차만 표시됐음)
