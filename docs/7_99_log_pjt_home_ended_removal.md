# 7.99. 개발로그 — PJT 홈 종료 프로젝트 카드 잔존 제거 (2026-10-07)

- 증상: 본섭 PC PJT 홈 상단에 "🏁 종료된 프로젝트" 카드(예: 청주 M15X CUB동 A/S)가 노출. 종료 PJT 전용 메뉴(5.1.0)와 중복.
- 원인: `renderPjtRegistry()`가 `pjt_registry`의 `status==='ended'` 문서를 `#pjt-registry-section`에 계속 렌더. 5.1.0에서 전용 뷰로 이전하며 이 호출부 렌더를 걷어내지 못함(모바일은 5.3.0·09-19에 이미 제외).
- 조치: `renderPjtRegistry()`를 홈 섹션 비우기로 단순화(호출부 4곳 유지). `pjtRegistryCard()`는 종료 PJT 뷰에서 사용하므로 유지.
- 반영: 본섭 직접(대표님 지시). 백업 `backup/v_pjthome_ended_20261007/index.html`. 테섭은 별도 미반영.
