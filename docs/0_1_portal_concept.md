# 0.1. 포털 — Concept & Structure

> 위치: 포털 `index.html`
> 최초 작성: 2026-07-01 · 작성: 춘식이(Claude)

---

## 개요

JH Solutions 사내 업무 포털. 단일 진입점(`https://jhsolutions5804.github.io/portal/`)에서 로그인 후, 업무 모듈을 iframe으로 임베드하여 통합 제공한다.

---

## 인증 흐름

```
로그인(회사 로고 + ID/PW, @jhsol.kr 자동)
  → 회원가입(@jhsol.kr 도메인만 허용)
  → 관리자(대표) 승인 (portal_users.status: pending → approved)
  → 승인 후 로그인 가능
```

- 도메인: `@jhsol.kr` (`DOMAIN`)
- 관리자: `jh.kim@jhsol.kr` (`ADMIN_EMAIL`)
- Firebase Auth + `portal_users/{uid}` (status, name, rank, dept, perms, admin 등)

---

## 모듈 구성 (MODULES)

| key | 메뉴 | 설명 | 앱 경로 |
|-----|------|------|---------|
| `plan` | 기획 | 영업·정산·회계 | `portal/gihoek/` |
| `hr` | 인사 | 급여·계약·근태·연차 | `portal/hr/` |
| `edoc` | 전자결재 | 업무일지·연차·구매·지출 | `portal/edoc/` |
| `pjt` | PJT 관리 | 진행 중 현장 관리 | `portal/pjt/` |

추가: 조직도(🏢, 전 사용자), Portal 관리(관리자 전용)

---

## 하위 탭 (SUBTABS)

각 모듈은 포털 사이드바에서 하위 탭으로 펼쳐지며, 선택 시 해당 앱의 `tab()`/`goTab()` 키로 직접 진입한다.

- **기획(plan)**: 홈 · 프로젝트 · 거래처 · 견적 · 정산 · 회계
- **인사(hr)**: 홈 · 근로자명부 · 근로계약서 · 연봉계약서 · 초과근로 · 급여명세서 · 퇴직금정산 · 연차현황
- **전자결재(edoc)**: 홈 · 결재함 · 업무일지 · 연차신청서 · 퇴직원서 · 재직증명서 · 구매품의서 · 지출결의서
- **PJT(pjt)**: PJT 홈 · P4 Ph2(FAB) · P4 Ph4(SUP)

---

## 임베드 메커니즘

- 모듈 클릭 → iframe(`emb-frame`)에 앱 URL 로드 (`?via=portal&tab=…`)
- **캐시 방지(N11)**: src에 `_cb=Date.now()` 추가 → 항상 최신 로드
- 같은 앱 내 탭 전환은 postMessage(`goTab`)로 재로드 없이 처리
- 권한별 메뉴 분기: `portal_users.perms` / `admin` 기준
