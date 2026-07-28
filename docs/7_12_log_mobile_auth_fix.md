# 7_12 개발로그 — 모바일 Auth 초기화 버그 수정 + PJT registry 연동 (2026-07-28)

## 배경

2026-07-27 배포한 Firestore 보안 규칙 강화(`request.auth != null` 필수)로 인해, 본섭·테섭 모바일 페이지 전체에서 `permission-denied`가 발생. 처음엔 다음 순서로 원인을 좁혀나감:

1. 계정 승인 상태(portal_users) 의심 → 데이터 정상 확인
2. 브라우저 로컬 캐시/보안 예외 의심 → 시크릿 모드로 재현되어 배제
3. `localStorage.jh_login_perms`의 UID와 Firestore `portal_users` 문서 UID 대조 → 완전 일치, 계정/데이터 모두 정상
4. 최종적으로 코드 감사 결과, **모바일 페이지들이 Firebase Auth를 아예 초기화하지 않는다**는 사실 확인 (`getAuth()`/`onAuthStateChanged()` 전무)

## 근본 원인

`m/pjt.html`, `hr.html`, `edoc.html`, `gihoek.html`, `account.html`, `admin.html` 전부:
```js
const app=initializeApp(firebaseConfig);
const db=getFirestore(app);
// getAuth() 호출 없음 → Firestore 요청에 인증 토큰이 실리지 않음
```
어제까지는 Firestore 규칙이 `request.auth`를 요구하지 않아 무증상이었으나, 규칙 강화 이후 모든 read/write가 거부됨. PC `index.html`은 자체 로그인 폼에서 `signInWithEmailAndPassword` + `onAuthStateChanged`로 Auth를 명시적으로 관리하고 있어 문제없었음.

## 수정 내용

6개 파일 모두 동일 패턴 적용:
```js
import { getAuth, onAuthStateChanged } from 'https://www.gstatic.com/firebasejs/10.12.0/firebase-auth.js';
...
const auth = getAuth(app);
...
let _authBooted=false;
onAuthStateChanged(auth, ()=>{
  if(_authBooted) return; _authBooted=true;
  // 기존 Firestore 구독/초기 렌더 코드 전부 이 안으로 이동
});
```
PC에서 로그인한 세션이 origin 공유 IndexedDB에 남아있어, `getAuth()` 초기화만으로 별도 재로그인 없이 인증 토큰이 자동으로 실린다.

## PJT registry 실시간 연동 (`m/pjt.html`)

- `SITE(key)` 헬퍼 신설: FAB/SUP(정적 SITES 객체) + 경량PJT(동적 `pjt_registry` 구독)를 공통 인터페이스로 통합
- `lightMeta` 상태: `pjt_registry` 컬렉션 `onSnapshot` 구독, `status!=='ended'`만 유지
- 홈 카드: 기존 FAB/SUP 카드 아래 경량PJT 카드 자동 추가 (보라색, 🧩 아이콘)
- 일정: `schedList()`/`schColl()`/`schDocRef()` 헬퍼로 FAB/SUP(top-level collection)와 경량PJT(`pjt_registry/{id}/schedules` 서브컬렉션) 경로 분기. `renderCalendar`/`saveSched`/`deleteSched`/`toggleSchedDone`/`openSchedForm`/`renderSchedDetail` 전부 이 헬퍼 경유하도록 일반화
- 근태·공수: `loadAtt`/`toggleAttend`/`setMd`에 경량PJT 분기 추가 (`pjt_registry/{id}/workers`+`attendance`+`manday`)
- `pjt.html?site=fab`/`?site=sup`/`?site=reg_{id}` 쿼리파라미터 딥링크 지원
- 제외 범위: 업무지시·보고(daily_reports 구조 상이), 공정/스테이지 체크 — 후속 작업

## 배포 순서

1. portal-test에 6개 파일(Auth fix) + pjt.html(registry 연동) 순차 배포, GitHub Pages 빌드 stuck 발견 → `.nojekyll` 터치 + 강제 빌드로 해결
2. 브라우저 로컬 문제(안전하지 않음 경고, 시간 오인)로 곁가지 디버깅 소요
3. portal_users 부트스트랩 순환 문제 의심 → Firestore 규칙에 자가부트스트랩 예외 추가(실제로는 원인 아니었으나 안전장치로 유지)
4. 최종 Auth 초기화 누락 확인 후 6개 파일 일괄 수정, 테섭 재배포 → 정상 확인
5. 본섭 배포: 7개 파일(pjt/home/hr/edoc/gihoek/account/admin) + index.html 버전코멘트

## 백업

`backup/v5.2.0/m/*.html` (배포 전 원본 7개)
