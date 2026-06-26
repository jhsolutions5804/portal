# 0.2a. 포털 기본 Rule — 디자인·레이아웃·배포

> 최초 작성: 2026-06-26 · 최종 수정: 2026-06-27 · 작성: 춘식이(Claude)
> 연속 문서: 0.2b (HTML 주의사항·공통 로직)

---

## 디자인 토큰

```css
--blue:   #1D5BA6;   /* 메인 블루 */
--navy:   #13335C;   /* 사이드바 배경 */
--blue-l: #5BA4CF;   /* 라이트 블루 */
--bg:     #F4F7FB;   /* 페이지 배경 */
--card:   #FFFFFF;   /* 카드 배경 */
--line:   #DDE4EF;   /* 구분선 */
--sub:    #5C6F8A;   /* 보조 텍스트 */
--mute:   #9AAABF;   /* 비활성 텍스트 */
--ok:     #16A34A;   /* 성공·초록 */
--warn:   #DC2626;   /* 경고·빨강 */
--amber:  #F59E0B;   /* 주의·노랑 */

font-family: -apple-system, 'Apple SD Gothic Neo', 'Pretendard', sans-serif;
/* PC: ≥900px / 모바일: <900px / 콘텐츠 최대너비: 840px */
```

---

## 레이아웃 (iframe 임베드 확정 방식)

```css
/* PC */
#s-app.shown      { flex-direction:row; height:100vh; overflow:hidden; }
.sidebar          { width:248px; flex-shrink:0; }
.main             { flex:1; height:100vh; overflow:hidden; }
#view-home        { flex:1; }
#view-home.off    { display:none !important; }
#view-embed       { flex:1; display:none; flex-direction:column; height:100vh; }
#view-embed.on    { display:flex; }
.embed-frame-wrap { flex:1; position:relative; overflow:hidden; }  /* position 필수! */
.embed-pad        { position:absolute; inset:0; display:flex; flex-direction:column; }
.embed-frame      { position:absolute; inset:0; width:100%; height:100%; border:none; }
```

> ⚠️ `embed-frame-wrap`에 `position:relative` 없으면 iframe 0높이 → 빈 화면

---

## 자동 로그아웃

```js
const AUTO_LOGOUT_MS = 30 * 60 * 1000;
let _autoLogoutTimer = null;
function resetAutoLogout(){
  if(!me) return;
  clearTimeout(_autoLogoutTimer);
  _autoLogoutTimer = setTimeout(()=>{
    toast('⏰ 30분 동안 활동이 없어 자동 로그아웃됩니다.');
    setTimeout(()=>doLogout(), 2000);
  }, AUTO_LOGOUT_MS);
}
['click','keydown','mousemove','touchstart','scroll'].forEach(evt=>{
  document.addEventListener(evt, resetAutoLogout, {passive:true});
});
```

---

## 포털 탭 전환 메시지 수신 (각 앱 공통)

```js
window.addEventListener('message', e => {
  const d = e.data;
  if (d?.source === 'jh-portal' && d?.action === 'goTab' && TABS[d.key]) {
    goTab(d.key);
  }
});
```

---

## 배포 명령어

```bash
TOKEN=$(cat /mnt/project/Github_토큰 | tr -d '[:space:]')

# 1. 최신 SHA 확인 (필수!)
SHA=$(curl -s -H "Authorization: token $TOKEN" \
  "https://api.github.com/repos/jhsolutions5804/portal/contents/<경로>/index.html" \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('sha',''))")

# 2. payload 생성 및 배포
python3 -c "
import base64, json
c = base64.b64encode(open('파일경로','rb').read()).decode()
json.dump({'message':'커밋메시지','content':c,'sha':'$SHA'}, open('gp.json','w'))
"
curl -s -X PUT -H "Authorization: token $TOKEN" -H "Content-Type: application/json" \
  "https://api.github.com/repos/jhsolutions5804/portal/contents/<경로>/index.html" \
  -d @gp.json
```

**배포 전 체크리스트**
1. GitHub에서 최신 SHA 재확인 (옛 사본 덮어쓰기 방지)
2. `node --check 파일.html` JS 문법 검증
3. `<div>` 균형 확인: open/close 태그 수 일치
4. 배포 후 1~2분 뒤 실제 URL 확인

---

