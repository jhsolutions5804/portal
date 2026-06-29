# 📒 gihoek_expenses 장부 등록 루틴

## 개요
영수증 OCR → 데이터 정리 → Python 스크립트 → Firebase 자동 등록

---

## 사전 준비 (최초 1회)

### 1. Python 설치
- https://www.python.org/downloads/ 에서 Python 3.11 이상 설치
- 설치 시 **"Add Python to PATH"** 반드시 체크

### 2. cryptography 라이브러리 설치
```
pip install cryptography
```

---

## 매월 루틴

### STEP 1. 춘식이에게 영수증 사진 전달
- 카카오톡으로 영수증 사진 묶음 전송
- 춘식이가 OCR → 카테고리 분류 → 검토표 작성

### STEP 2. 검토 및 삭제 확정
- 춘식이가 보여주는 표에서 제외할 항목 번호 지정
- "이대로 등록해" 하면 다음 단계로

### STEP 3. 스크립트 다운로드 & 실행 (터미널)
```
curl -o upload.py https://raw.githubusercontent.com/jhsolutions5804/portal/main/scripts/upload_expenses.py
python upload.py
```

- 영수증이 많아서 2차로 나뉘면:
```
curl -o upload2.py https://raw.githubusercontent.com/jhsolutions5804/portal/main/scripts/upload_expenses2.py
python upload2.py
```

### STEP 4. 결과 확인
- 터미널에서 ✅ 20/20건 완료 확인
- 포탈 → 기획 → 회계 → 비용 장부에서 등록 확인

---

## 데이터 구조 (gihoek_expenses 컬렉션)

| 필드 | 타입 | 예시 |
|---|---|---|
| date | string | "2026-06-01" |
| cat | string | 식대 / 유류비 / 공구·자재비 / 차량유지비 / 사무용품 / 기타 / 임대료 / 세금 / 급여 / 용역비 |
| vendor | string | "셀렉토커피 고덕원희캐슬점" |
| supply | integer | 15637 |
| vat | integer | 1563 |
| total | integer | 17200 |
| pay | string | 개인카드 / 법인카드 / 현금 / 계좌이체 |
| pjt | string | "p4ph2" (P4 Ph2 FAB) |
| note | string | "아메리카노x3, 비타부스터x1" |

---

## 공급가·부가세 역산 공식
- 공급가 = round(합계 / 1.1)
- 부가세 = 합계 - 공급가
- 면세 품목(의료비 등)은 supply=합계, vat=0

---

## Firebase 정보
- **Project**: p4ph2-fab-506a7
- **Collection**: gihoek_expenses
- **Auth**: Service Account (프로젝트 파일에 저장됨)

---

## 스크립트 위치
- `scripts/upload_expenses.py` — 1차 등록용 템플릿
- `scripts/upload_expenses2.py` — 2차 등록용 템플릿

> 매번 등록 전 춘식이가 데이터를 업데이트해서 GitHub에 올려줌
> 터미널에서 curl로 받아서 python으로 실행하면 끝

---

## 이력

| 날짜 | 건수 | 내용 |
|---|---|---|
| 2026-06-29 | 20건 | 6월 1차 (6/1~6/22) |
| 2026-06-29 | 18건 | 6월 2차 (6/16~6/29) |
