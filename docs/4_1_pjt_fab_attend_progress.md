# 4.1. PJT 관리 — P4 Ph2 FAB (근태 · 공정)

> 앱: `portal/pjt/index.html`
> Firestore: `worker_manday`, `progress_checks_{날짜}`, `pjt_workers_fab`
> 최초 작성: 2026-07-01 · 작성: 춘식이(Claude)

---

## 4.1.4 근태 (attend)

기술인(현장 작업자)의 출역·공수를 관리한다.

### 화면 구성
- 좌측: 기술인 출역 현황 + 공수 입력 (`+`/`-` 버튼 또는 직접 입력칸)
- 출역 인원 카운트 배지(`att-worker-count`)
- "📋 이달 공수 집계표 보기" 모달(`openKongsuModal`)

### 공수 데이터 (worker_manday)
```js
worker_manday/{pKey}:    // pKey = 기간/월 키
{
  ...기술인별 공수 데이터
}
```
- `getDoc(doc(db,'worker_manday', pKey))`로 조회
- 이달 공수는 백그라운드 preload(`_mandayCache`)로 근태 탭 미방문 시에도 홈 KPI에 표시

### 홈 KPI 연동
- 이달 누적 공수(`home-manday`), 오늘 출역(`home-att`) 등 홈 대시보드에 집계 표시
- PC 상단 누적공수(`pc-manday-total`)

### 기술인 명단 (pjt_workers_fab)
- 추가·삭제 가능 (`order`로 정렬)
- 제거해도 기존 공수·출역 데이터는 유지

---

## 4.1.5 공정 (progress)

작업 구역(zone)별 공정 진행을 체크한다.

### 공정 데이터 (progress_checks)
```js
progress_checks_{날짜키}/{zoneId}:    // 예: progress_checks_2026-06-23 / {zoneId}
{
  ...구역별 공정 체크 데이터
}
```
- 날짜별로 컬렉션 분리(`progress_checks_` + dateKey)
- 구역(zone) 단위 문서: `doc(db, 'progress_checks_'+dateKey, zoneId)`
- 조회 `getDoc`, 저장 `setDoc`, 갱신은 zone별 ref로 직접 수정

### 화면
- 2분할 레이아웃 (구역 목록 / 체크 상세)
- `window._renderProgressUI()`로 구독 갱신 시 리렌더
