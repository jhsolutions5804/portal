# 7.69. 개발로그 — 강제 PC 화면 → 모바일 전환 버튼 복구 (포털 홈)

> 2026-09-30 · 춘식이(Claude) · 대표님 제보 → 테섭·본섭 동시 반영

## 증상

- 모바일에서 “PC 화면으로 보기”를 누른 뒤, PC 화면 안의 “📱 모바일 화면”(우측 하단) 버튼과 사이드바 하단 “모바일 화면으로 전환” 버튼이 눌러도 반응이 없음.

## 원인

- 두 버튼은 `jhSwitchToMobile()`을 호출하지만 **함수 정의가 어디에도 없었음**(브라우저 오류 `jhSwitchToMobile is not defined`).
- 테섭 커밋 `505ebbc`(2026-09-28, “강제 PC 화면의 모바일 전환 버튼을 우측 하단(작업탭 위)으로 이동”)가 버튼 위치 코드를 고치면서 `jhEnsureMobileFab` 뒤에 있던 아래 정의를 함께 삭제함(이전 `f1bfea7`에는 존재).
  ```js
  window.jhSwitchToMobile=function(){ try{ localStorage.removeItem('jh_force_pc'); }catch(e){} location.href='m/home.html'; };
  ```
- 그 상태로 오늘 06:53 본섭 반영(`ecd040c`, 강제 PC 모드)에 넘어가 **테섭·본섭 모두 동일 증상**.

## 수정

- 삭제된 정의를 원문 그대로 `jhEnsureMobileFab` 다음에 복원(추가 4줄, 삭제 0). 동작: 강제 PC 설정(`jh_force_pc`) 해제 → `m/home.html` 이동.
- 본섭은 본섭 파일에 그대로 얹어 Firebase 설정 교체가 필요 없음.

## 검증

- 재현: 수정 전 테섭·본섭 모두 두 버튼이 이동하지 않고 같은 오류 발생(jsdom).
- 수정 후: 우측 하단 버튼·사이드바 버튼 모두 PC 모드 해제 + 모바일 홈 이동(테섭·본섭 각각).
- 같은 종류의 누락 점검: `jh*` 함수 호출 15종 전수 확인 → 정의 없는 것은 이 함수 하나뿐. script 문법 검사 OK.
- 배포본: 저장소 원본·백업 일치, 테섭·본섭(GitHub Pages·portal.jhsol.kr) 서빙본에서 함수 정의 확인.
- 실제 휴대폰 확인은 대표님 확인 대기.

## 배포 · 백업

- portal-test·portal `index.html` (각 저장소 `backup/20260930_switch_mobile_fix/before|after/`).
- 본섭 반영은 “모바일 월간 공수 팀 단가 수정”과 분리해 버튼 수정만 먼저 반영(대표님 지시). 월간 공수 관련은 별도(`7_65_log_manday_removal.md`).

## 참고

- 이 결함은 테섭 검증 단계(9/28)부터 있었음. 이후 수정 시 함수 삭제 여부를 확인하는 정의·호출 대조(위 15종 점검 방식)를 권장.
