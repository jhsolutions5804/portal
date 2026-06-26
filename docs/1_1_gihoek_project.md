# 1.1. 기획 — 프로젝트

> Firestore 컬렉션: `gihoek_projects`
> 최초 작성: 2026-06-26 · 작성: 춘식이(Claude)
> 최종 수정: 2026-06-26

---

## Firestore 스키마

```js
gihoek_projects/{id}:
{
  code:      string,           // 프로젝트 코드
  name:      string,           // 프로젝트명
  client:    string,           // 발주처
  type:      'fcu' | 'general',
  status:    'run' | 'done',
  createdAt: serverTimestamp
}
```

---

## 주요 기능

- CRUD (생성·수정·삭제)
- 프로젝트 카드에 **견적 / 청구 / 지급 / 손익** 요약 표시
  - 손익 = 청구 − 지급

---

## 프로젝트 상세 (`pjtDetail`)

| 섹션 | 내용 |
|------|------|
| 요약 4칸 | 견적 / 청구 / 지급 / 손익 |
| 견적 내역 | 연결된 견적서 목록 |
| 정산 내역 | 연결된 정산서 목록 (청구·지급 구분, 상태 표시) |

> ⚠️ 구버전 5칸(견적/청구/지급/잔금/손익)에서 **잔금 칸 제거** (2026-06-26)
> 미수금은 정산 탭 상단 요약에서 확인

**정산 내역 상태 표시**
- 유효(active): 기본
- 완결(done): 초록 태그
- 폐기(void): 회색 태그

---

## 미수금 정의

```
미수금 = 청구액(pjtBilled) − 수금액(pjtDone)
       = 대금청구 누계 − 완결된 청구서 합계
```

- **완결(done) 처리된 대금청구서 = 수금 완료로 간주**
- 헬퍼: `pjtDone(pid)` — 완결 청구서 합계 (수금액)
- 헬퍼: `pjtDue(pid)` — 미수금 (`pjtBilled − pjtDone`)
- 표시 위치: 정산 탭 상단 요약 카드 / 기획 홈 KPI

---

## 집계 규칙

- **유효 견적 집계**: `status !== 'void' && status !== 'closed'`
- **청구 누계(pjtBilled)**: `status !== 'void'` (완결 포함, 폐기만 제외)
- **수금액(pjtDone)**: `status === 'done'` (완결 처리된 청구서)
- **미수금(pjtDue)**: `pjtBilled − pjtDone`
- **지급 집계**: `docType === 'payment' && status !== 'void'`
