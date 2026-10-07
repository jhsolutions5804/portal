/* 연명부 원본 정리 롤백 — portal_secrets 의 백업(roster_backup_20261007__*)으로 master_worker_private 를 정리 전 상태로 되돌린다.
 * 사용: GOOGLE_APPLICATION_CREDENTIALS=서비스계정.json FIREBASE_ADMIN_PATH=firebase-admin경로 node roster_rollback.js [--with-info] [--apply]
 *   기본은 비교만(모의 실행). --apply 로 private 를 백업본으로 덮어쓴다. --with-info 를 붙이면 master_worker_info 도 백업 시점으로 되돌린다(그 뒤에 새로 저장한 내용은 사라짐).
 * 값은 출력하지 않는다. 이 파일에는 개인정보가 들어 있지 않다. */
const admin=require(process.env.FIREBASE_ADMIN_PATH); admin.initializeApp({projectId:'p4ph2-fab-506a7'}); const db=admin.firestore();
const TAG='roster_backup_20261007'; const apply=process.argv.includes('--apply'); const withInfo=process.argv.includes('--with-info');
const stable=v=>JSON.stringify(v,(k,x)=>{ if(x&&x.toMillis&&x.constructor&&/Timestamp/.test(x.constructor.name)) return {__ts:x.toMillis()}; if(x&&typeof x==='object'&&!Array.isArray(x)) return Object.keys(x).sort().reduce((o,key)=>{o[key]=x[key];return o;},{}); return x; });
(async()=>{
  const idx=await db.collection('portal_secrets').doc(TAG+'__INDEX').get(); if(!idx.exists){ console.error('백업 목록이 없습니다.'); process.exit(1); }
  const I=idx.data(); const jobs=[]; for(const id of I.privateIds) jobs.push(['private','master_worker_private',id]); if(withInfo) for(const id of I.infoIds) jobs.push(['info','master_worker_info',id]);
  let diff=0,wrote=0; for(const [kind,col,id] of jobs){ const b=await db.collection('portal_secrets').doc(TAG+'__'+kind+'__'+id).get(); if(!b.exists){ console.error('백업 문서 없음:',kind,id); process.exit(1); }
    const cur=await db.collection(col).doc(id).get(); const same=cur.exists&&stable(cur.data())===stable(b.data().data); if(!same) diff++;
    if(apply&&!same){ await db.collection(col).doc(id).set(b.data().data); wrote++; } }
  console.log('대상',jobs.length,'문서 | 백업과 다른 문서',diff,apply?('| 되돌린 문서 '+wrote):'| (모의 실행 — 쓰지 않음, 실행하려면 --apply)'); process.exit(0);
})().catch(e=>{console.error('오류:',e.message);process.exit(1)});
