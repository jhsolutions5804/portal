import json, time, base64, urllib.request, urllib.parse
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

SA = {
  "client_email": "firebase-adminsdk-fbsvc@p4ph2-fab-506a7.iam.gserviceaccount.com",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDLn4Srhr8IrWMI\ncxhen8Np7Mg0bDeFfA3jKDak2PqPfcDaLu53P4gvU4DP4bzccxIrsO/l300KmFvh\nFw+ZyGkTXlm8if2cXgqMeIu2pDbDRELW4ejEJllXuCJctmCvOP8uRh2eU+B89pXf\nEJ01E4kB21hUbg01znyD7e9TvW7ScKAaPQuLs5gtB94kAEDnLx4/pRJOQNQpYqIj\nMtQ4TH+IIBBfotzUyvYdYvej6U6jf3jSvldEfF/5DzSil1hX7pG5af0HBA1FFKk8\nrNxOiFJHmK9c+7RHbFbXUHAqQElNN6k/qiPzwakz/Ep3Ni1XxfcpHc4ny9NuwyM/\nRmY865jNAgMBAAECggEADmBFyqJpzGAJdOhDWTLoZgscm27kgJ0gkeAd84eKMSVM\nv1q+5VZr9ANuPb8PSXUqXEFSvqUEWHInUn4BUPcwS/jGVyRa7nZJQl+kZZG0eBbS\nrT8n4uleN249ptQNgXGBuq+imbIMUGZMcIJIxx2I98OXueZHMnxQmDPtSLlAIMVI\nbbQRDMqyQrIa8zsOJFEWhHkFat26lDgk710C5W2Bmrk8kIgFQGUsFQIft2RYsm5Z\nVyaLGlmeqE3+w4xmqqYLzZV97UBvq7s8TjKnEBMS8vGfoSeHQFsP/jBbGaK9Ql/i\nN7t+XVuUuegwHTfu9VYZJFJxAs8wSCy05XD0phsHVQKBgQD9lq2q2WlgevsuxTMD\nByLiJtTtuenaTvdXr/OV3DOorKO1reyf9LBHCZf9Dq39oQp5QXxDGVuqakRNUF4h\nCQaGrZg59vmw7jfaR0S4m0Jx9rPE3e/oJ71mpGEVbCYEpQ50+VU3Kouax/bppevN\n+DM9Lgkso1ed/oY1/g8Qus7AAwKBgQDNjzTuV6142XpO6oDQXJO9pIpTZIdc5GSy\nxQYhntre7CXquWziuVoB5Hn+pgw6VnEHAkxpNm4OeR+bKRspTsGe9PPtEgMd+dzA\nRdrt7+d8gRuojuqUFWAFpu/yc2tiTltMTt4+A85QEZC/LwM2Md6b+FZXa4upmx4M\n1qnpgXdy7wKBgDvn7prfxW8PXmtMFqLueqUmO0L1mnMCGJhUbpzGakW8kugGcFHR\nQhtl/su/PgcelhTTDYHkaa02cXA6PiJbuXjzZXS8DXxoqjUchPV/aBD4ELu/Gj+j\ns7CdwHmJFOof++xSQnlHybcE6iWEFtKPgbtANtaet8IRMK9sly6Ckvj1AoGAdqiP\nDnKQUa2Am+NkXmLCaft8We0y8l1o/4UaJ/gyMfKxZJCLGUmTenowLd4eOuLBNiGO\niEGCQFqM8x1Eb5Dl1eNil1wJbplYY6kvWqBcyRMiKyfso3S/TCP0aMlVmJbQvvjb\n84Jw6ulo2+PAf91DulcdSDNtmIdRTmnwBTnWAQMCgYEAhVh+Dodv+yTqyxpX0WQn\n698tIzH0Xk0TROgb+77ARAcGE2yGaudVaBFctpUacVG/IQrhKohBClnduay8FX4e\ndWleYgoFjOYGbDHyTz2IgkqnTFLPFFilK0RBmSS9IUZLLtOAuo6zeCmJCnqxOE0M\nnLiUWpAkqvl0I9dqu/2bX6o=\n-----END PRIVATE KEY-----\n"
}

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
