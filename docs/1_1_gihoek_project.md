# 1.1. 기획 — 프로젝트

> Firestore 컬렉션: `gihoek_projects`
> 최초 작성: 2026-06-26 · 작성: 춘식이(Claude)
> 최종 수정: 2026-08-29 (PJT관리 자동연동)

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

---

## PJT관리 자동 연동 (2026-08-29)

### 배경
기획(상업적 계약/견적 단위)과 PJT 관리(현장 운영/공정·공수 단위)가 별도 프로젝트 목록으로 관리되어 서로 어긋나는 문제가 있었음(예: 기획 "H17L" ↔ PJT관리 "화성 17L 개보수 현장"이 같은 프로젝트인데 이름이 달라 서로 인지 못함, PJT관리에만 있고 기획엔 없는 경량 PJT 존재).

### 연동 방향 결정
**기획 → PJT관리** 단방향. 이유: 계약/견적이 확정되는 시점(기획)이 현장 착수(PJT관리)보다 항상 선행하고, 견적서·정산서가 기획 소속 기능이라 프로젝트의 원본 정체성을 기획이 가져야 함. PJT관리가 독립적으로 프로젝트를 만들면 계약 없는 현장이 시스템에 등록될 위험이 있음.

### 스키마 추가
```js
gihoek_projects/{id}:
{
  ...(기존 필드),
  linkPjt:     'auto' | 'p4ph2' | 'p4ph4' | 'none' | 'reg_{pjt_registry문서id}',
  progProfile: string,   // 'p4ph2'|'p4ph4'|'' — 경량PJT(reg_*)는 빈 문자열(공정 자동연동 미지원, 향후 과제)
  mandayCol:   string,   // 'worker_manday'|'ph4_manday'|''
}
```

### 동작 방식 (`openPjtForm` / `savePjt`)
- "연동 PJT" 드롭다운: P4 Ph2/Ph4(고정 2개) + `pjt_registry`(경량 PJT, `status!=='ended'`)에서 실시간으로 불러온 전체 목록(`refreshLinkPjtOptions`) + "🆕 새 PJT관리 항목 자동 생성"(신규 등록 시 기본값) + "연동 없음".
- **신규 프로젝트 등록 시** `linkPjt==='auto'`(기본값)면, 저장 시 `pjt_registry`에 동일한 이름으로 경량 PJT 문서를 `addDoc`으로 자동 생성하고 그 문서 ID를 `reg_{id}` 형태로 `linkPjt`에 저장.
- **기존 PJT관리 항목과 연결**하려면 드롭다운에서 `reg_xxx` 옵션을 직접 선택(자동생성 아님, 중복 방지).

### 한계 / 향후 과제
- 경량 PJT(`reg_*`) 연동은 현재 "연결"만 되고, P4 Ph2/Ph4처럼 공정률·공수 데이터를 자동정산에 끌어오는 심화 연동(`progProfile`/`mandayCol` 기반)은 아직 구현 안 됨 — `type:'general'`(품목 직접입력)로만 운용됨.
- 기존 어긋난 데이터(H17L↔화성17L, M15X)는 스크립트가 아닌 화면에서 관리자가 직접 "연동 PJT" 드롭다운으로 재연결 필요(Firestore 직접 접근 불가로 인한 제약).
