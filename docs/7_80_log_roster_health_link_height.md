# 7.80. 개발로그 — 연명부 검진 결과 링크 행 높이 고정 (연명부 2.2.2)

> 2026-10-01 · 춘식이(Claude) · 본섭 직접 반영 (테섭에는 Storage가 없어 PDF 첨부 확인 불가)

## 증상
- 검진 결과 PDF를 올리면 해당 근로자 행만 높이가 늘어남(검진 칸이 2줄 → 3줄).

## 원인
- `healthBadge()`가 `📄 결과` 링크를 별도 `<div>`(새 줄)로 출력.

## 수정
- 링크를 만료일(`~YYYY-MM-DD`) 줄 오른쪽에 인라인 배치, 만료일이 없으면 단독 줄. 새 CSS `.pdflink`(11px, 밑줄 없음, hover 시 밑줄).
- 모바일 카드 목록도 같은 함수를 쓰므로 함께 적용. 변경 범위: `pjt_roster/index.html`의 `healthBadge` + CSS 2줄.

## 검증
- `<script type="module">` node --check 통과, CSS 괄호 깊이 0·음수 없음, diff는 해당 함수와 CSS 2줄뿐.
- 화면 확인은 본섭에서 PDF 첨부된 행(김종화)으로 진행.

백업: `backup/v2.2.2/pjt_roster/index.html`

## 테섭 정합 (2026-10-01)
- portal-test `pjt_roster/index.html`에 같은 논리 패치를 독립 적용(2.2.2). 파일 통째 복사 없이 적용해 테섭 Firebase 설정 유지. 두 저장소의 연명부 코드 차이는 Firebase 설정 블록뿐임을 diff로 확인. portal-test에도 `backup/v2.2.2/pjt_roster/` 백업.
