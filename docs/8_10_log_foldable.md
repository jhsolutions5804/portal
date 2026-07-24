# 8_10 · 폴더블(Z Fold) 펼침 시 PC 화면 유지 (r1)

**작업일**: 2026-07-24
**대상**: `index.html`, `m/home.html`
**요청 계기**: 대표님(Z Fold7) — "펼치면 PC 환경으로 보이게 못하나? 조회가 안 되잖아"

## 원인
`showApp()`이 `navigator.userAgent`의 "Mobi" 포함 여부만으로 PC/모바일을 결정. 폴더블 펼침 상태에서도 UA는 그대로 모바일이라 항상 `m/home.html`로 강제 이동되고 있었음.

## 수정
- `index.html`의 `showApp()`: UA뿐 아니라 **화면 폭(900px)** 도 함께 판단하도록 변경 — 모바일 UA + 좁은 화면일 때만 모바일로 전환
- `localStorage` 기반 수동 오버라이드(`jh_force_pc` / `jh_force_mobile`) 추가
- PC 사이드바 "📱 모바일 화면으로 보기", `m/home.html` "🖥️ PC 화면으로 전환" 버튼 추가

## 안전성 확인
대표님이 배포 전 "기존 코드 안 깨지냐" 재확인 요청 → 데스크톱/일반 폰은 영향 없고, "모바일 UA + 넓은 화면" 케이스만 새로 PC 유지되도록 바뀐다는 점을 설명 후 승인받고 진행.

## 검증
- `node --check` 통과 (index.html 2개 스크립트 블록, m/home.html)

## 배포
- 대표님 승인("ㅇㅇ") 후 **테스트서버 생략, 본섭 직접 배포**
- 커밋: `index.html` `65f33d8`(로직) + 버전주석 갱신, `m/home.html` `0623d31`
- 백업: `backup/v2.6.6/index.html`, `backup/v2.6.6/m/home.html`
- 문서: `docs/0_1_portal_concept.md`(PC/모바일 라우팅 섹션 신규), `docs/7_1_log_portal_r4b.md`
