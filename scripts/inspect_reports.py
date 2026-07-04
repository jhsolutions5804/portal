#!/usr/bin/env python3
# 업무지시/보고 데이터가 실제로 어느 컬렉션·필드에 저장돼 있는지 확인하는 스크립트
# 사용법:
#   pip install firebase-admin
#   python3 inspect_reports.py [서비스계정키.json]
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
    print("  python3 inspect_reports.py /경로/p4ph2-fab-506a7-firebase-adminsdk-fbsvc-f84b0371ec.json")
    sys.exit(1)

print(f"[키] {key}\n")
cred = credentials.Certificate(key)
firebase_admin.initialize_app(cred)
db = firestore.client()

# 1) 최상위 컬렉션 전체 나열 (report/daily/지시/보고 관련만 강조)
print("=" * 60)
print("최상위 컬렉션 목록 (업무 관련 강조)")
print("=" * 60)
all_names = []
for col in db.collections():
    name = col.id
    all_names.append(name)
    low = name.lower()
    mark = "  <== 관련?" if any(k in low for k in ["report", "daily", "ph4", "instruct", "지시", "보고"]) else ""
    print(f"  {name}{mark}")

# 2) 관련 컬렉션 샘플 문서 + 필드 출력
print("\n" + "=" * 60)
print("관련 컬렉션 샘플 (문서ID · 필드 · 값)")
print("=" * 60)
for name in all_names:
    low = name.lower()
    if not any(k in low for k in ["report", "daily", "ph4", "instruct", "지시", "보고"]):
        continue
    try:
        docs = list(db.collection(name).limit(3).stream())
    except Exception as e:
        print(f"\n[{name}] 조회 오류: {e}")
        continue
    if not docs:
        continue
    print(f"\n### 컬렉션: {name}  (샘플 {len(docs)}건)")
    for d in docs:
        data = d.to_dict() or {}
        keys = list(data.keys())
        print(f"  - 문서ID: {d.id}")
        print(f"    필드: {keys}")
        # 값 일부 표시 (길면 자름)
        for k, v in data.items():
            sv = str(v)
            if len(sv) > 80:
                sv = sv[:80] + "…"
            print(f"      {k} = {sv}")

print("\n완료. 위 결과(특히 '관련 컬렉션 샘플' 부분)를 그대로 붙여 주시면,")
print("업무지시/보고가 실제로 어디에 있는지 확정해서 정확히 연동하겠습니다.")
