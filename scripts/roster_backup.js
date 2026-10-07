/* 연명부 원본 정리 전 백업 — master_worker_private(13) + master_worker_info(3)를 portal_secrets(관리자 전용) 아래에 그대로 복사한다. 값은 출력하지 않는다. */
const admin=require(process.env.FIREBASE_ADMIN_PATH); admin.initializeApp({projectId:'p4ph2-fab-506a7'}); const db=admin.firestore(); const FV=admin.firestore.FieldValue;
const TAG='roster_backup_20261007';
const stable=v=>JSON.stringify(v,(k,x)=>{ if(x&&x.toMillis&&x.constructor&&/Timestamp/.test(x.constructor.name)) return {__ts:x.toMillis()}; if(x&&typeof x==='object'&&!Array.isArray(x)) return Object.keys(x).sort().reduce((o,key)=>{o[key]=x[key];return o;},{}); return x; });
(async()=>{
  const sources=[['master_worker_private','private'],['master_worker_info','info']]; const plan=[];
  for(const [col,kind] of sources){ const s=await db.collection(col).get(); s.forEach(d=>plan.push({col,kind,id:d.id,data:d.data()})); }
  console.log('백업 대상:',plan.filter(p=>p.kind==='private').length,'private /',plan.filter(p=>p.kind==='info').length,'info');
  let batch=db.batch(),n=0;
  for(const p of plan){ batch.set(db.collection('portal_secrets').doc(TAG+'__'+p.kind+'__'+p.id),{kind:'roster_backup',takenAt:FV.serverTimestamp(),sourceCollection:p.col,sourceId:p.id,data:p.data}); n++; }
  batch.set(db.collection('portal_secrets').doc(TAG+'__INDEX'),{kind:'roster_backup_index',takenAt:FV.serverTimestamp(),
    note:'연명부 원본 정리(clean) 직전 상태의 master_worker_private·master_worker_info 전체 복사본. 롤백: roster_rollback.js. 관리자 전용(portal_secrets). 개인정보 포함.',
    privateIds:plan.filter(p=>p.kind==='private').map(p=>p.id),infoIds:plan.filter(p=>p.kind==='info').map(p=>p.id),count:n}); 
  await batch.commit(); console.log('백업 문서 기록:',n,'+ 목록 1');
  // 읽어서 원본과 전부 같은지 비교
  let bad=0; for(const p of plan){ const b=await db.collection('portal_secrets').doc(TAG+'__'+p.kind+'__'+p.id).get(); if(!b.exists||stable(b.data().data)!==stable(p.data)){ bad++; console.log('불일치:',p.col,p.id); } }
  console.log(bad?'❌ 백업 불일치 '+bad+'건':'✅ 백업 '+plan.length+'건이 원본과 완전히 같습니다(Timestamp 포함)');
  process.exit(bad?1:0);
})().catch(e=>{console.error('오류:',e.message);process.exit(1)});
