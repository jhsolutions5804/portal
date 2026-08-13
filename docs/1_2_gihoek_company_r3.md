# 1.2. 기획 — 거래처

> Firestore 컬렉션: `gihoek_companies`
> 최초 작성: 2026-07-01 · 최종 수정: 2026-08-13(r3) · 작성: 춘식이(Claude)

---

## Firestore 스키마

```js
gihoek_companies/{id}:   // id = 'co_{timestamp}'
{
  company:      string,    // 회사명 (필수)
  ceo:          string,    // 대표자
  bizno:        string,    // 사업자번호
  address:      string,    // 주소
  contacts:     [          // 담당자 목록
    { name: string, tel: string, email: string }
  ],
  roleSupplier: boolean,   // 발행처 역할 (우리가 발행)
  roleClient:   boolean    // 수신처 역할 (거래 상대)
}
```

---

## 역할 (중복 선택 가능)

한 업체가 발행처·수신처 역할을 동시에 가질 수 있다.

| 역할 | 의미 | 사용처 |
|------|------|--------|
| `roleSupplier` | 발행처 (우리가 발행) | 견적·정산의 **발행처** 드롭다운 |
| `roleClient` | 수신처 (거래 상대) | 견적·정산의 **수신처** 드롭다운 |

> 역할이 하나도 없으면 견적·정산 드롭다운에 나타나지 않는다 (저장은 확인 후 가능).

---

## 담당자 (contacts)

- 업체별로 담당자를 여러 명 등록 (이름·전화·이메일)
- 견적·정산 작성 시 업체를 고르면, 그 업체의 담당자를 드롭다운으로 선택 가능
- 선택한 담당자 정보는 문서 스냅샷(`issuerContact`/`clientContact`, `contact`/`contactTel`/`contactEmail`)으로 저장 → 발행 후에도 보존
- 담당자 헬퍼: `ctSnap(cid, name)` — 업체 id + 담당자명으로 연락처 스냅샷 생성

---

## 핵심 함수

| 함수 | 동작 |
|------|------|
| `renderComp()` | 거래처 목록 화면 |
| `editComp(id)` | 등록/수정 폼 (id 없으면 신규). 담당자는 `_cfContacts` 임시배열로 편집 |
| `addContact()` / `renderContactRows()` | 담당자 행 추가·렌더 |
| `saveComp(id)` | 저장. id 없으면 `co_{timestamp}` 신규 생성. `contacts`는 빈 행 제거 후 저장 |
| `delComp(id)` | 삭제 (기존 견적·정산에 저장된 스냅샷 정보는 유지됨) |

---

## 데이터 시드 / 마이그레이션

- `gihoek_companies`가 비어 있으면, 기존 거래처·발행처 데이터에서 역할을 합쳐 통합 생성
- 기존 데이터도 없으면 `SEED_COMPANIES` 기본값 시드

---

## 버그 수정 이력

- **2026-08-13(r3) — 진짜 원인**: r2에서 고친 blur 배열 미동기화는 실제 원인이 아니었음. 진짜 원인은 `fmtTel`/`fmtTelBlur` 함수가 `<script type="module">` 내부에 일반 함수로 선언되어 있어, HTML 인라인 이벤트 핸들러(`oninput`, `onblur`)에서 호출 시 `ReferenceError: fmtTel is not defined`가 발생 → 전화번호 입력 자체가 배열에 반영되지 않던 것. `window.fmtTel = fmtTel`, `window.fmtTelBlur = fmtTelBlur`로 전역 노출 추가하여 해결. 동일 파일 내 다른 인라인 핸들러 함수 전수 조사 결과 이 두 개만 해당(그 외 `zoneGuess` 등은 템플릿 렌더링 시점에 모듈 스코프에서 미리 평가되므로 문제 없음).
- **2026-08-13(r2)**: 담당자 전화번호 입력란(`onblur="fmtTelBlur(this)"`)에서 8자리 전화번호 자동 "010" 접두 처리 시, 화면 표시값만 재포맷되고 실제 저장 배열(`window._cfContacts[i].tel`)은 갱신되지 않던 버그 수정. `fmtTelBlur(el, idx)`로 인덱스를 전달받아 배열도 함께 동기화하도록 변경.

---

## 구독

```js
onSnapshot(collection(db,'gihoek_companies'), …)
  → companies 배열 갱신 (회사명 가나다순 정렬)
  → 거래처 탭이면 renderComp() 재호출
```
