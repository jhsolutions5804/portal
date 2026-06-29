# 업데이트 알고리즘 (2026-06-29 확정)

> JH Solutions 포털 — 코드 업데이트 표준 절차
> 작성: 춘식이(Claude) · 최초: 2026-06-29

---

## 전체 흐름도

```
[업데이트 요청]
       │
       ▼
┌─────────────────────┐
│  1. Logic 검토       │
│  - 구현 가능 여부     │
│  - 기존 코드 영향 분석│
│  - 충돌 여부 확인     │
└──────────┬──────────┘
           │
     문제 있음?
     ┌──Yes──▶ 2. 대안 제시 및 검토
     │              │
     │         확정 후 재검토
     │              │
     No ◀───────────┘
     │
     ▼
┌─────────────────────┐
│  3. 최신 코드 내려받기│
│  - GitHub GET (최신)  │
│  - local 저장        │
│  - local test 진행   │
│    · Unit Test       │
│    · Integration Test│
│    · Acceptance Test │
│    · JS 문법 검증     │
└──────────┬──────────┘
           │
     이상 있음?
     ┌──Yes──▶ 4. Logic 재검토 → 3번으로
     │
     No
     │
     ▼
┌─────────────────────┐
│  5. test server 배포 │
│  jhsolutions5804     │
│  .github.io/portal-  │
│  test/              │
└──────────┬──────────┘
           │
     문제 있음?
     ┌──Yes──▶ 6. local 코드 수정 → 5번으로
     │
     No
     │
     ▼
┌─────────────────────┐
│  7. main server 배포 │
│  jhsolutions5804     │
│  .github.io/portal/  │
└──────────┬──────────┘
           │
     문제 있음?
     ┌──Yes──▶ 8. test server로 이동 → 6번으로
     │
     No
     │
     ▼
┌─────────────────────────────────────────┐
│  9. 마무리                               │
│  - main + test server 코드 버전 최신화   │
│  - MD rev. (기능문서 + 개발로그 세트)     │
│  - 통합 스냅샷 백업 (버전 번호 사용자 확인)│
└─────────────────────────────────────────┘
```

---

## 단계별 체크리스트

### 1단계 — Logic 검토
- [ ] 구현 목적·기능 명확히 파악
- [ ] 수정 대상 파일·함수 특정
- [ ] 기존 코드와 충돌 여부 분석
- [ ] Firestore 권한 이슈 여부 확인
- [ ] postMessage 필요 여부 확인 (hr→portal 쓰기 시)

### 2단계 — 대안 제시 (필요 시)
- [ ] 최소 2개 이상 옵션 제시
- [ ] 각 옵션의 장단점·구현 범위 명시
- [ ] 사용자 선택 후 확정

### 3단계 — Local Test
- [ ] GitHub GET으로 최신 파일 내려받기 (SHA 확인)
- [ ] Unit Test 작성 및 실행 (`node`)
- [ ] Integration Test 실행
- [ ] Acceptance Test (실제 코드 적용 후 검증)
- [ ] `node --check` JS 문법 검증
- [ ] 테스트 결과 사용자에게 보고

### 4단계 — Logic 재검토 (이상 발생 시)
- [ ] 오류 원인 정확히 특정
- [ ] 수정 방향 재설계
- [ ] 3단계부터 재시작

### 5단계 — Test Server 배포
- [ ] `portal-test` 저장소에 PUT
- [ ] Firebase 컬렉션: `test_` 접두어 사용
- [ ] 배포 후 URL 확인:
      `https://jhsolutions5804.github.io/portal-test/`
- [ ] 사용자에게 테스트 요청

### 6단계 — Local 코드 수정 (test server 문제 시)
- [ ] 오류 메시지·콘솔 로그 확인
- [ ] 원인 특정 후 코드 수정
- [ ] 3단계 test 재수행
- [ ] 5단계 test server 재배포

### 7단계 — Main Server 배포
- [ ] `portal` 저장소에 PUT
- [ ] 배포 SHA 확인
- [ ] 사용자에게 main 배포 완료 보고

### 8단계 — Main Server 문제 시
- [ ] 즉시 test server로 이동 (main 롤백 검토)
- [ ] 6단계부터 재시작

### 9단계 — 마무리
- [ ] main + test server 코드 버전 동일 여부 확인 (SHA 비교)
- [ ] 기능 문서 rev. (`docs/`)
- [ ] 개발 로그 rev. (`docs/`)
- [ ] 통합 스냅샷 백업 (`backup/v{ver}/`)
- [ ] 백업 버전 번호 사용자 확인 후 저장

---

## 서버 정보

| 구분 | URL | 저장소 | Firebase 컬렉션 |
|------|-----|--------|----------------|
| **main** | `jhsolutions5804.github.io/portal/` | `jhsolutions5804/portal` | 실제 컬렉션 |
| **test** | `jhsolutions5804.github.io/portal-test/` | `jhsolutions5804/portal-test` | `test_` 접두어 |

---

## 규칙

- main server 직접 배포는 test server 검증 후에만 허용
- test server 없이 main 배포는 **긴급 hotfix**에 한해 예외 허용
  (단, 사용자 명시적 승인 필요)
- 모든 배포는 사용자 보고 후 진행 (임의 배포 금지)
