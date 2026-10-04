import json, time, base64, urllib.request, urllib.parse
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

import os, sys

def load_sa():
    """서비스 계정 키(JSON)는 저장소에 두지 않는다 — 키 파일 경로를 환경변수 FIREBASE_SA_KEY_FILE 로 지정한다."""
    p = os.environ.get('FIREBASE_SA_KEY_FILE')
    if not p or not os.path.isfile(p):
        sys.exit('환경변수 FIREBASE_SA_KEY_FILE 에 서비스 계정 키(JSON) 파일 경로를 지정하세요. (키 파일은 저장소·메신저에 올리지 말고 개인 PC에만 보관)')
    d = json.load(open(p, encoding='utf-8'))
    return {"client_email": d["client_email"], "private_key": d["private_key"]}

SA = load_sa()

def b64url(data):
    if isinstance(data, str): data = data.encode()
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()

def get_token(sa):
    now = int(time.time())
    header = b64url(json.dumps({"alg":"RS256","typ":"JWT"}))
    payload = b64url(json.dumps({
        "iss":sa["client_email"],"sub":sa["client_email"],
        "aud":"https://oauth2.googleapis.com/token",
        "iat":now,"exp":now+3600,
        "scope":"https://www.googleapis.com/auth/datastore"
    }))
    msg = f"{header}.{payload}".encode()
    key = serialization.load_pem_private_key(sa["private_key"].encode(), password=None)
    sig = key.sign(msg, padding.PKCS1v15(), hashes.SHA256())
    jwt = f"{header}.{payload}.{b64url(sig)}"
    data = urllib.parse.urlencode({
        "grant_type":"urn:ietf:params:oauth:grant-type:jwt-bearer","assertion":jwt
    }).encode()
    with urllib.request.urlopen(urllib.request.Request("https://oauth2.googleapis.com/token", data=data)) as r:
        return json.loads(r.read())["access_token"]

PROJECT = "p4ph2-fab-506a7"

print("토큰 발급 중...")
token = get_token(SA)
print("토큰 발급 완료!\n")

# 전체 문서 조회
all_docs = []
url = f"https://firestore.googleapis.com/v1/projects/{PROJECT}/databases/(default)/documents/gihoek_expenses?pageSize=300"
req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
with urllib.request.urlopen(req) as r:
    data = json.loads(r.read())
all_docs = data.get("documents", [])
print(f"총 {len(all_docs)}건 조회됨")

# 중복 탐지: date+vendor+total 기준으로 첫 번째 등장만 남기고 나머지 삭제
seen = {}
to_delete = []

for doc in all_docs:
    f = doc["fields"]
    date = f.get("date",{}).get("stringValue","")
    vendor = f.get("vendor",{}).get("stringValue","")
    total = f.get("total",{}).get("integerValue","")
    key = f"{date}|{vendor}|{total}"
    doc_id = doc["name"].split("/")[-1]
    doc_name = doc["name"]

    if key in seen:
        to_delete.append((doc_name, doc_id, date, vendor, total))
    else:
        seen[key] = doc_id

print(f"중복 감지: {len(to_delete)}건\n")

if not to_delete:
    print("중복 없음! 깨끗한 상태입니다.")
else:
    for doc_name, doc_id, date, vendor, total in to_delete:
        print(f"  삭제 대상: {date} | {vendor} | {total}원 | ID: {doc_id}")

    print(f"\n총 {len(to_delete)}건 삭제합니다...")
    deleted = 0
    for doc_name, doc_id, date, vendor, total in to_delete:
        url = f"https://firestore.googleapis.com/v1/{doc_name}"
        req = urllib.request.Request(url, method="DELETE",
            headers={"Authorization": f"Bearer {token}"})
        try:
            with urllib.request.urlopen(req) as r:
                r.read()
            print(f"  ✅ 삭제: {date} {vendor} {total}원")
            deleted += 1
            time.sleep(0.1)
        except Exception as e:
            print(f"  ❌ 실패: {date} {vendor} - {e}")

    print(f"\n완료: {deleted}/{len(to_delete)}건 삭제")
