# 3.3. 전자결재 — 퇴직원서 · 재직증명서 · 구매품의서 · 지출결의서

> Firestore 컬렉션: `edoc_resign`, `edoc_cert`, `edoc_purchase`, `edoc_expense`
> 최초 작성: 2026-07-01 · 작성: 춘식이(Claude)

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
    { key, label, type, ph?, opts? }   // type: text|textarea|date|number|select
  ]
}
```

### 문서별 설정

| dtype | 명칭 | 결재자 | 회람 | 주요 필드 |
|-------|------|--------|------|----------|
| `resign` | 퇴직원서 | 김종화·김영희·송지훈 | 김민서 | 퇴직예정일, 퇴직사유 |
| `cert` | 재직증명서 | 김종화 | — | 용도, 발급언어, 부수 |
| `purchase` | 구매품의서 | 김종화 | — | 품목, 수량, 단가, 공급업체, 목적, 필요일, **참고 링크(다중)** |
| `expense` | 지출결의서 | 김종화 | — | 지출일, 구분, 금액, 거래처, 목적, 증빙 |

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

## 참고 링크 다중입력 (구매품의서) — 3.3.x

구매품의서에 `refUrls` 필드(type='urls', 선택). 참고 자료 URL을 여러 개 입력.

- `+ 링크 추가` 버튼으로 행 무제한 추가, `−` 버튼으로 삭제 (`addUrlRow`)
- 저장: `.url-input` 값들을 배열로 수집(빈 값 제외)
- 출력(`fmtDocVal`): URL 배열이면 전체 주소 대신 "링크"(1개)/"링크1·링크2…"(복수) 하이퍼링크로 표시, 새 탭 열림
