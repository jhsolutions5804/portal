/* 연명부 원본 정리 — master_worker_private 에서 master_worker_info 로 옮긴 항목을 지운다. 은행·계좌·일당·팀 단가는 남긴다.
 * 조건: ① 정리 전 백업(portal_secrets/roster_backup_20261007__*)이 있고 현재 private 와 같을 것 ② 지울 항목이 info 에 이미 있을 것(info 가 최신이므로 값이 다른 것은 허용). 값은 출력하지 않는다. */
const admin=require(process.env.FIREBASE_ADMIN_PATH); admin.initializeApp({projectId:'p4ph2-fab-506a7'}); const db=admin.firestore(); const FV=admin.firestore.FieldValue;
const TAG='roster_backup_20261007'; const ADMIN_KEYS=['bank','account','dailyRate','teamRate']; const apply=process.argv.includes('--apply');
const stable=v=>JSON.stringify(v,(k,x)=>{ if(x&&x.toMillis&&x.constructor&&/Timestamp/.test(x.constructor.name)) return {__ts:x.toMillis()}; if(x&&typeof x==='object'&&!Array.isArray(x)) return Object.keys(x).sort().reduce((o,key)=>{o[key]=x[key];return o;},{}); return x; });
(async()=>{
  const idx=await db.collection('portal_secrets').doc(TAG+'__INDEX').get(); if(!idx.exists){ console.error('중단: 백업 목록이 없습니다.'); process.exit(1); }
  const [ps,is]=await Promise.all([db.collection('master_worker_private').get(),db.collection('master_worker_info').get()]); const info={}; is.forEach(d=>info[d.id]=d.data());
  const todo=[]; let blocked=0;
  for(const d of ps.docs){ const b=await db.collection('portal_secrets').doc(TAG+'__private__'+d.id).get();
    if(!b.exists||stable(b.data().data)!==stable(d.data())){ console.error('중단: 백업과 현재가 다릅니다 →',d.id); process.exit(1); }
    const mv=Object.keys(d.data()).filter(k=>!ADMIN_KEYS.includes(k)); if(!mv.length) continue;
    const missing=mv.filter(k=>!(info[d.id]&&k in info[d.id])); if(missing.length){ blocked++; console.error('중단: info 에 없는 항목이 있습니다 →',d.id,missing.join(',')); continue; }
    todo.push({id:d.id,keys:mv}); }
  if(blocked){ process.exit(1); }
  console.log('정리 대상 문서',todo.length,'| 지울 항목 합계',todo.reduce((a,t)=>a+t.keys.length,0),'| 남는 항목: 은행·계좌·일당·팀 단가 등 관리자 전용');
  if(!apply){ console.log('모의 실행 — 지우지 않았습니다. 실행하려면 --apply'); process.exit(0); }
  const batch=db.batch(); todo.forEach(t=>{ const upd={}; t.keys.forEach(k=>{ upd[k]=FV.delete(); }); batch.update(db.collection('master_worker_private').doc(t.id),upd); });
  await batch.commit(); console.log('✅ 정리한 문서:',todo.length); process.exit(0);
})().catch(e=>{console.error('오류:',e.message);process.exit(1)});
