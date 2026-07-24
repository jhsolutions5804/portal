#!/usr/bin/env python3
# 전자결재 초과근로(edoc_overtime) 승인 건이 인사 overtime 컬렉션에
# 실제로 연동됐는지 확인하는 진단 스크립트
#
# 사용법:
#   pip install firebase-admin
#   python3 check_overtime_link.py [서비스계정키.json]
#   (키 파일명을 생략하면 현재 폴더의 p4ph2-fab-506a7-... 파일을 자동으로 찾습니다)

import sys, os, glob
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
except ImportError:
    print("firebase-admin 이 필요합니다. 먼저:  pip install firebase-admin")
    sys.exit(1)

# 키 파일 찾기
key = None
if len(sys.argv) > 1:
    key = sys.argv[1]
else:
    cands = glob.glob("p4ph2-fab-506a7-*firebase-adminsdk*.json") or glob.glob("*firebase-adminsdk*.json")
    if cands:
        key = cands[0]
if not key or not os.path.exists(key):
    print("서비스계정 키 파일을 찾을 수 없습니다. 인자로 경로를 주세요:")
    print("  python3 check_overtime_link.py /경로/p4ph2-fab-506a7-firebase-adminsdk-fbsvc-f84b0371ec.json")
    sys.exit(1)

print(f"[키] {key}\n")
cred = credentials.Certificate(key)
firebase_admin.initialize_app(cred)
db = firestore.client()

print("=" * 70)
print("1) edoc_overtime 컬렉션 — 전체 문서 (상태·연동 플래그 포함)")
print("=" * 70)

edoc_docs = []
for doc in db.collection("edoc_overtime").stream():
    d = doc.to_dict()
    d["_id"] = doc.id
    edoc_docs.append(d)

edoc_docs.sort(key=lambda d: d.get("date", ""), reverse=True)

for d in edoc_docs:
    status = d.get("status", "?")
    linked = d.get("linkedToOvertime", False)
    mark = ""
    if status == "approved" and not linked:
        mark = "  <== ⚠️ 승인됐는데 linkedToOvertime=False (연동 누락 의심)"
    print(f"  [{d['_id']}] {d.get('date','?')} {d.get('name','?')}({d.get('rank','')}) "
          f"{d.get('hours','?')}h {d.get('amount','?')}원 status={status} linked={linked}{mark}")

print(f"\n총 {len(edoc_docs)}건")

print("\n" + "=" * 70)
print("2) hr overtime 컬렉션 — 전체 문서")
print("=" * 70)

hr_docs = []
for doc in db.collection("overtime").stream():
    d = doc.to_dict()
    d["_id"] = doc.id
    hr_docs.append(d)

hr_docs.sort(key=lambda d: d.get("date", ""), reverse=True)

for d in hr_docs:
    print(f"  [{d['_id']}] {d.get('date','?')} {d.get('name','?')}({d.get('rank','')}) "
          f"{d.get('hours','?')}h {d.get('amount','?')}원 reason={d.get('reason','')!r}")

print(f"\n총 {len(hr_docs)}건")

print("\n" + "=" * 70)
print("3) 대조 — 승인된 edoc_overtime 건 중 hr overtime에 매칭되는 문서가 있는지")
print("   (매칭 기준: workerId + date + hours 일치)")
print("=" * 70)

def key_of(d):
    return (d.get("workerId", ""), d.get("date", ""), round(float(d.get("hours", 0) or 0), 2))

hr_keys = set(key_of(d) for d in hr_docs)

problem_found = False
for d in edoc_docs:
    if d.get("status") != "approved":
        continue
    k = key_of(d)
    matched = k in hr_keys
    flag = "✅ 매칭됨" if matched else "❌ 매칭 안 됨 — 인사에 미반영"
    if not matched:
        problem_found = True
    print(f"  [{d['_id']}] {d.get('date','?')} {d.get('name','?')} {d.get('hours','?')}h "
          f"linked={d.get('linkedToOvertime')} → {flag}")

print("\n" + "=" * 70)
if problem_found:
    print("⚠️  인사(overtime)에 반영 안 된 승인 건이 있습니다. 위 ❌ 표시된 문서ID를 확인해주세요.")
else:
    print("✅ 승인된 초과근로 건은 모두 인사 overtime 컬렉션에 정상 반영되어 있습니다.")
print("=" * 70)
