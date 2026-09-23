# 0.5. 포털 — 다중 작업탭 (하단 탭바)

> 대상: `index.html` (포털 셸 전체 — 특정 모듈이 아닌 임베드 프레임워크 자체)
> 최초 작성: 2026-09-23 · 작성: 춘식이(Claude)

---

## 요청

대표님 — 업무 보다 보면 이 메뉴 저 메뉴 다 봐야 하는데, 화면 하단에 탭이 생기게 해서 여러 메뉴를 오가며 업무 볼 수 있게 해달라. 탭은 최대 10개 정도.

## 배경 — 기존 구조의 한계

포털은 기획/인사/전자결재/PJT 각 모듈을 `iframe#emb-frame` **하나**에 로드하는 구조였다(`openModule`). 다른 메뉴를 열면 그 iframe의 `src`를 바꿔치기해서 기존 화면(스크롤 위치, 입력하던 내용, 열어둔 모달 등)이 통째로 사라졌다 — 메뉴를 자주 오가는 실사용 패턴과 안 맞았다.

## 구현

**핵심 아이디어**: iframe을 하나가 아니라 **탭 개수만큼** 만들어 두고, 활성 탭만 `display:block`, 나머지는 `display:none`으로 숨긴다. 화면 전환이 곧 "재로딩 없는 표시 전환"이 되어 상태가 보존된다.

- **탭 단위**: 모듈(`m.key`, 예: `hr`)이거나 개별 워크스페이스(`overrideUrl`, 예: 특정 PJT `pjt/`). 같은 모듈 안에서 서브탭(예: 인사의 근로자명부→급여명세서)을 바꾸는 것은 새 탭을 만들지 않고 **기존처럼 `postMessage`로 그 탭의 iframe 안에서만** 처리한다(`{source:'jh-portal', action:'goTab', key}` — 각 모듈의 `window.addEventListener('message', ...)` 수신부는 무수정).
- **`openModule(m, tab, overrideUrl)` 재작성**:
  - 이미 열려 있는 탭(`jhTabId(m, overrideUrl)`로 식별)이면 **재로딩 없이** 그 탭을 활성화만 하고, 서브탭 지정이 있으면 postMessage.
  - 없으면 새 iframe(`jhMakeFrame`)을 만들어 `#emb-frame-stack`에 추가하고 탭 목록(`jhTabs`)에 등록.
  - 이미 10개(`JH_TABS_MAX`)면 새로 열지 않고 안내(`탭은 최대 10개까지 열 수 있습니다. 먼저 하단에서 탭을 닫아주세요.`).
- **`jhActivateTab(id)`**: 모든 탭의 iframe display를 토글하고, 상단 타이틀·"새 창에서 열기" 링크·사이드바 활성 표시(`_activeMod`/`_activeSub`)를 갱신한 뒤 `showView('embed')`.
- **`jhCloseTab(id)`**: 해당 iframe을 DOM에서 제거하고 탭 목록에서 삭제. 닫은 탭이 활성 탭이었으면 인접 탭으로 전환하고, 마지막 탭이었으면 포털 홈으로 돌아간다.
- **`jhRenderTabbar()`**: `#jh-tabbar`(하단, `.main` 안쪽이라 사이드바와 안 겹침)에 탭 목록을 그린다. 탭이 없으면 숨김.
- **세션 복원**: `jhSaveTabs()`가 탭 메타(iframe DOM 제외, url·이름·서브탭 등)를 `sessionStorage`에 저장하고, 로그인 직후(`enterPortal()` → `jhRestoreTabs()`) 같은 세션 안에서 새로고침해도 열려 있던 탭 목록과 iframe이 복원된다. 단, 화면은 강제로 전환하지 않고(포털 홈에서 시작) 활성 탭 표시도 초기화한다 — 클릭해야 보여준다. iframe 안 입력 내용까지 복원되진 않는다(iframe 자체를 새로 불러오기 때문).

## 제약·주의사항

- 탭 개수 상한은 상수 `JH_TABS_MAX = 10`.
- `showPjtHome()`/`showPjtEndedView()`(PJT 홈·종료 PJT 뷰)는 iframe이 아닌 포털 셸 자체 화면이라 탭 시스템 대상이 아니다(기존과 동일하게 동작).
- 권한 체크(`기획/인사는 관리자만`, `월간 공수는 관리자만`)는 `openModule` 최상단에 그대로 유지 — 탭 재사용 여부와 무관하게 매번 검사한다.
- `_embUrl`/`_activeMod`/`_activeSub` 등 기존 전역 상태는 탭 전환 시점마다 활성 탭 기준으로 갱신해, 탭 도입 이전 코드(사이드바 하이라이트 등)가 그대로 동작한다.

## 관련 함수 위치 (index.html)

| 함수 | 역할 |
|------|------|
| `openModule(m, tab, overrideUrl)` | 탭 오픈/재사용 진입점 (기존 함수, 내부만 재작성) |
| `jhTabId(m, overrideUrl)` | 탭 고유 id 생성 (`m:<key>` 또는 `ov:<url>`) |
| `jhMakeFrame(name, fullUrl)` | 탭용 iframe 생성 (절대 위치 스택) |
| `jhActivateTab(id)` / `jhCloseTab(id, evt)` | 탭 전환 / 닫기 |
| `jhRenderTabbar()` | 하단 탭바 렌더 |
| `jhSaveTabs()` / `jhRestoreTabs()` | sessionStorage 저장·복원 (`enterPortal()`에서 1회 호출) |

## 검증

jsdom으로 탭 관리 로직만 추출해 37개 시나리오 검증(관리자 권한, 탭 생성/재사용/전환/닫기, iframe 재생성 없음, postMessage 서브탭 전환, 10개 초과 차단, 세션 저장/복원) — 전부 통과.
