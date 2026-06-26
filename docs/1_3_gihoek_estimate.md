# 1.3. 기획 — 견적

> Firestore 컬렉션: `gihoek_estimates`
> 최초 작성: 2026-06-26 · 작성: 춘식이(Claude)

---

## Firestore 스키마

```js
gihoek_estimates/{id}:
{
  pjtId:      string,
  no:         string,          // EST-YYYY-NNN
  baseNo:     string,          // 개정 전 원본 번호
  rev:        number,          // 개정 차수
  status:     'active' | 'void' | 'closed',
  date:       string,
  title:      string,
  items:      [{name, spec, qty, price, amount}],
  clientId:      string,
  client:        {...스냅샷},   // company, ceo, bizno, tel, email, address, contact
  clientContact: string,        // 담당자명 (별도 저장)
  issuerId:      string,
  issuer:        {...스냅샷},   // company, ceo, bizno, tel, email, address, contact
  issuerContact: string,        // 담당자명 (별도 저장)
  authorDept: string,
  authorName: string,
  authorEmail:string,
  authorUid:  string,
  replacedBy: string,          // 개정 시 신 번호
  createdAt:  serverTimestamp
}
```

---

## 상태 정의

| status | 의미 | 유효 집계 |
|--------|------|----------|
| `active` | 유효 | ✅ |
| `closed` | 종결 | ❌ |
| `void` | 폐기 | ❌ |

`isActive(e)` = `e.status !== 'void' && e.status !== 'closed'`

---

## 핵심 동작

**품목 양방향 계산**
- 수량×단가 → 금액
- 금액 → 단가 (÷수량)
- 입력 중 재렌더 안 함 (커서 튐 방지)

**합계금액 직접 수정**
- 마지막 품목 줄이 차액 흡수
- 공급가 = 합계 / 1.1

**작성자 정보**
- 포털 계정 기본값, 건마다 수정 가능
- PDF 하단 표기

---

## 개정 발행

```
원본 status → 'void'
개정본 신규 생성 (no = baseNo-r2…)
집계는 유효본(active)만
```

---

## 발행처 / 수신처 담당자

- 거래처(`gihoek_companies`)의 `contacts[]` 배열에 등록된 담당자 목록을 드롭다운으로 선택
- 선택한 담당자명은 `issuerContact` / `clientContact` 로 별도 저장
- `client` / `issuer` 스냅샷 내 `contact` 필드에도 함께 저장 → 견적 열람·PDF에 표시

### 담당자 드롭다운 동작

| 상황 | 표시 |
|------|------|
| 거래처에 담당자 등록됨 | 담당자 선택 드롭다운 (활성) |
| 거래처에 담당자 없음 | "담당자 없음 (거래처 탭에서 추가 가능)" — disabled |
| 발행처/수신처 미선택 | 드롭다운 미표시 |

### ⚠️ 개발 주의사항 — window 전역 등록 필수

발행처/수신처 `<select>`의 `onchange`에서 `drawEstForm()`을 인라인으로 호출하므로,
`<script type="module">` 내부 함수는 반드시 `window`에 전역 등록해야 함.

```js
// 필수 — 없으면 업체 변경 시 ReferenceError → 담당자 드롭다운 갱신 안 됨
window.drawEstForm    = function(){ drawEstForm(); };
window.drawSettleForm = function(){ drawSettleForm(); };
```

---

## 종결 (`closeEst / reopenEst`)

- "🔒 종결" 버튼 → `status: 'closed'`, `closedAt: serverTimestamp()`
- "종결 취소" → `status: 'active'`
- 종결 견적은 유효 카운트·합계에서 제외
- 표시: 파랑 태그·배너
