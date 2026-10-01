# 7.88. 개발로그 — 포털 홈 캘린더 날짜 칸 너비 고정 (포털 build 20261001f)

> 2026-10-01 · 춘식이(Claude) · 대표님: "포탈 홈에 있는 calender 칸 너비 고정하자. 이게 뭐야.." → 테섭 확인 후 "본섭"

## 원인
- 7열 그리드가 `repeat(7,1fr)`라 열의 최소 너비가 내용(줄바꿈 없는 공휴일 라벨)에 맞춰 늘어남 → 공휴일 칸만 넓어지고 나머지가 좁아짐.

## 수정 (`index.html`)
- `repeat(7,1fr)` 10곳 → `repeat(7,minmax(0,1fr))`, `.pjt-cal-cell`에 `min-width:0; overflow:hidden`.

## 검증
- JS 문법(ESM 모듈 검사)·CSS 괄호 깊이 0. 변경은 해당 줄 26줄. 본섭 파일은 테섭 설정·worker_private 코드 혼입 없음(독립 패치). 화면 확인은 대표님이 테섭에서 진행.

## 배포·백업
- 테섭 build 20261001e → 본섭 build 20261001f. 백업 `backup/v_home_calwidth_20261001f/index.html`. 롤백은 직전 커밋(build 20261001c).
