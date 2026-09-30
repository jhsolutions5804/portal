# 7.54. 개발로그 — PJT(Ph2) 공수표 월 중 퇴사자 누락 수정 (v4.10.10)

> 작성: 2026-09-30 · 작성: 춘식이(Claude) · 긴급 핫픽스 (테섭·본섭 동시 반영, 대표님 지시)

## 증상
- 월 중 퇴사자가 있으면 퇴사 전 출역일 공수까지 공수표(이달 공수 집계표)에서 통째로 빠짐.

## 원인
- v4.10.9에서 공수표 대상자를 `getActiveWorkersForDate(_ksDateKey())`로 걸렀는데, `_ksDateKey()`가 **해당 월 말일**을 반환 → 월 중 퇴사자는 말일 기준 퇴사자로 판정되어 시트 전체에서 제외.

## 수정 (`pjt/index.html`)
- `_ksMonthWorkers()` 신설: **월 1일 기준** 재직자(월 중 퇴사자 포함)를 시트 대상자로 사용 (openKongsuModal / renderKongsuTabs / renderKongsuSheet).
- `_ksActiveOn(w, dateKey)` 신설: 일자별 재직 판정 (퇴사일 당일부터 제외 — 기존 규칙 유지).
- 팀장 시트: 일별 `x/N명`의 분자·분모·공수합계를 그날 재직자 기준으로 계산.
- 개별 시트: 퇴사일 이후 일자 공수는 0 처리.

## 반영
- portal-test `7b5eba1` · portal `8713e93` · 백업 `backup/v4.10.10/pjt/`
- 범위: Ph2(pjt)만. pjt_ph4 / pjt_light 동일 로직 여부는 미확인·미반영.
