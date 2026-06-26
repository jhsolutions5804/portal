# 7.1. 개발 로그 — 포털 홈

> `portal/index.html` 변경 이력
> 최초 작성: 2026-06-26 · 작성: 춘식이(Claude)

---

## 커밋 이력

| SHA | 날짜 | 내용 |
|-----|------|------|
| `783f99e0` | 2026-06-25 | C안 도메인 통합 — 4개 앱 단일 저장소 마이그레이션 |
| `1cc89682` | 2026-06-25 | 부서 선택 선택사항 + 자동 로그아웃 30분 |
| `05308797` | 2026-06-25 | 계정 생성 부서(optgroup)·직급 드롭박스 추가 |
| `3dfbd4bc` | 2026-06-25 | Portal 관리 신설 — 직원 계정 생성·접근권한, 가입 승인 삭제 |
| `e01ae853` | 2026-06-25 | 전자결재(edoc) iframe 모듈 추가 |
| `e743bcd8` | 2026-06-25 | 사이드바에 전자결재 결재함 메뉴 추가 |
| `dfe662b2` | 2026-06-25 | 레이아웃 — 사이드바-메인 간격 제거 |
| `0f624aa5` | 2026-06-25 | 인사 사이드바에 연차 현황(7) 추가 |
| `43fa1d51` | 2026-06-25 | renderDocMain 전역 등록 — 뒤로가기 버튼 작동 수정 |
| `57473bf4` | 2026-06-25 | 직원 비밀번호 변경 UI 신설 (Secondary App) |
| `6eee2bfa` | 2026-06-25 | _pw 자동 동기화 + 기존 계정 최초 1회 입력 처리 |
| `843f3a40` | 2026-06-25 | 기존 계정 최초 1회 현재PW 입력란 조건부 표시 |
| `2e7c6855` | 2026-06-26 | A4+B6 portal↔workers 계정 연동 |
| `24aeb7e2` | 2026-06-26 | PJT홈 공정률 FAB PAST 상수 합산 |
| `2c934054` | 2026-06-26 | A4+B6 portal↔workers 연동 최종 |
| `3d1bfd16` | 2026-06-26 | PJT홈 레이아웃 재구성 (2단: 카드+패널) |
| `bd76eff8` | 2026-06-26 | 홈 대시보드: 결재함+Outlook 2단 카드 / 메뉴카드 제거 |
| `0a8dc3ec` | 2026-06-26 | fix: MSAL 초기화 타이밍 문제 수정 |
| `45d58bcd` | 2026-06-26 | fix: MSAL ESM dynamic import 방식으로 전환 |
| `26942bcf` | 2026-06-26 | fix: MSAL uid별 인스턴스 격리 — 계정별 Outlook 독립 연결 |

---

## 주요 이슈 & 해결

| 이슈 | 해결 |
|------|------|
| 직원 상세 `ed-dept`에 guest 부서 누락 | `deptOpts`에 `<option value="guest">guest</option>` 추가 |
| PJT홈 공정률 0% (PAST 상수 미포함) | `loadPjtStats`에 `FAB_PAST_PROGRESS` 상수 삽입 후 Firestore와 병합 |
| iframe 빈 화면 | `embed-frame-wrap`에 `position:relative` 추가 |
| 배포 SHA 충돌 | 배포 전 반드시 GET으로 최신 SHA 재확인 |
| Outlook "연결 중" 멈춤 | MSAL CDN script 태그 → ESM dynamic import 방식으로 전환 |
| MSAL 중복 initialize | `_msalInitialized` 플래그 → `_msalApps[uid]` 캐싱으로 개선 |
| 계정 전환 시 타 계정 Outlook 노출 | me.uid 기반 MSAL 인스턴스 격리 + 로그아웃 시 캐시 강제 삭제 |

---

## Outlook 카드 구현 상세 (2026-06-26)

### Azure AD 앱 정보
```
앱 이름:    jhsolutions_portal
Client ID:  97f0a368-a746-42f9-8782-38ac8cc0962c
Tenant ID:  548fcb48-1ab8-4c47-8242-bc098ea80416
권한:       Mail.Read, User.Read (관리자 동의 완료)
```

### 구현 방식
- **MSAL ESM import**: `https://esm.sh/@azure/msal-browser@3.28.0`
- **계정 격리**: `_msalApps[me.uid]` — 포털 uid별 독립 인스턴스
- **sessionStorage 태깅**: `msal_portal_uid_{homeAccountId}` = uid
- **로그아웃 연동**: `doLogout()` → `clearMsalCache()` 호출

### 홈 대시보드 구조
```
.home-dash (grid 1fr 1fr)
  ├── 전자결재 결재함 카드 (좌)
  │     └── 내 차례 문서 최대 5건
  │     └── 전자결재 결재함 전체 보기 버튼
  └── Outlook 메일 카드 (우)
        ├── 읽지 않은 메일 수 뱃지
        ├── 최근 메일 5건 목록
        └── Outlook Web 열기 버튼
```

### Outlook 카드 상태 3가지
| 상태 | 표시 |
|------|------|
| 미연결 | Microsoft 계정 연결 버튼 |
| 연결됨 (미확인 있음) | 빨강 숫자 뱃지 + 메일 목록 |
| 연결됨 (모두 읽음) | 초록 ✓ 뱃지 + 메일 목록 |
