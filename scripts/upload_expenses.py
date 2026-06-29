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

def fs_add(token, project, col, fields):
    url = f"https://firestore.googleapis.com/v1/projects/{project}/databases/(default)/documents/{col}"
    body = json.dumps({"fields": fields}).encode()
    req = urllib.request.Request(url, data=body, method="POST",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

print("토큰 발급 중...")
token = get_token(SA)
print("토큰 발급 완료!")
PROJECT = "p4ph2-fab-506a7"

EXPENSES = [
    {"date":"2026-06-01","cat":"식대","vendor":"셀렉토커피 고덕원희캐슬점","supply":15637,"vat":1563,"total":17200,"pay":"개인카드","pjt":"p4ph2","note":"아메리카노x3, 비타부스터x1, 돌체라떼x1"},
    {"date":"2026-06-02","cat":"식대","vendor":"셀렉토커피 고덕원희캐슬점","supply":8636,"vat":864,"total":9500,"pay":"개인카드","pjt":"p4ph2","note":"아메리카노x2, 유자자x1"},
    {"date":"2026-06-04","cat":"식대","vendor":"아지매숯불갈비 송탄점","supply":122727,"vat":12273,"total":135000,"pay":"개인카드","pjt":"p4ph2","note":"숯불갈비 등"},
    {"date":"2026-06-04","cat":"식대","vendor":"카페 쉼","supply":5727,"vat":573,"total":6300,"pay":"개인카드","pjt":"p4ph2","note":"아메리카노 ICE x3"},
    {"date":"2026-06-04","cat":"유류비","vendor":"망향(하)주유소","supply":123636,"vat":12364,"total":136000,"pay":"개인카드","pjt":"p4ph2","note":"경유 68.41L"},
    {"date":"2026-06-05","cat":"식대","vendor":"백다방 평택고덕SBC점","supply":15273,"vat":1527,"total":16800,"pay":"개인카드","pjt":"p4ph2","note":"아메리카노x4, 아이스티x1, 원조커피x1, 카페라떼x1"},
    {"date":"2026-06-06","cat":"유류비","vendor":"에스씨에너지 용이주유소","supply":136364,"vat":13636,"total":150000,"pay":"개인카드","pjt":"p4ph2","note":"고급유 63.56L"},
    {"date":"2026-06-07","cat":"식대","vendor":"와일드그라스","supply":6364,"vat":636,"total":7000,"pay":"개인카드","pjt":"p4ph2","note":"과테말라 엔트레 Iced x1"},
    {"date":"2026-06-08","cat":"식대","vendor":"백다방 평택고덕SBC점","supply":8182,"vat":818,"total":9000,"pay":"개인카드","pjt":"p4ph2","note":"초코라떼(ICED)x1, 미숫가루(우유)x1"},
    {"date":"2026-06-08","cat":"사무용품","vendor":"다이소 평택장당점","supply":18182,"vat":1818,"total":20000,"pay":"개인카드","pjt":"p4ph2","note":"니트릴장갑, 거품비누, 핸드워시, 껌 등"},
    {"date":"2026-06-09","cat":"사무용품","vendor":"워크업 평택용이점","supply":33636,"vat":3364,"total":37000,"pay":"개인카드","pjt":"p4ph2","note":"유니보스 상의, 핫파일털이 신사"},
    {"date":"2026-06-09","cat":"식대","vendor":"이마트24 R고덕에스타워점","supply":9091,"vat":909,"total":10000,"pay":"개인카드","pjt":"p4ph2","note":"비타500 100x10"},
    {"date":"2026-06-11","cat":"식대","vendor":"셀렉토커피 부세키캠프2호점","supply":6091,"vat":609,"total":6700,"pay":"개인카드","pjt":"p4ph2","note":"아메리카노 선라이즈x1, 그릭톡스x1"},
    {"date":"2026-06-12","cat":"식대","vendor":"이마트24 R고덕에스타워점","supply":10909,"vat":1091,"total":12000,"pay":"개인카드","pjt":"p4ph2","note":"오로나민Cx9, 말랑카우딸기우유x1"},
    {"date":"2026-06-15","cat":"유류비","vendor":"(주)운정구도일 주유소","supply":136364,"vat":13636,"total":150000,"pay":"개인카드","pjt":"p4ph2","note":"고급유 64.185L"},
    {"date":"2026-06-16","cat":"식대","vendor":"셀렉토커피 고덕원희캐슬점","supply":9091,"vat":909,"total":10000,"pay":"개인카드","pjt":"p4ph2","note":"고소한 아메리카노x4"},
    {"date":"2026-06-17","cat":"식대","vendor":"우리집","supply":36364,"vat":3636,"total":40000,"pay":"개인카드","pjt":"p4ph2","note":"제육볶음x2, 김치찌개x2"},
    {"date":"2026-06-18","cat":"유류비","vendor":"고덕동일주유소","supply":128888,"vat":12889,"total":141777,"pay":"개인카드","pjt":"p4ph2","note":"경유 70.995L"},
    {"date":"2026-06-19","cat":"식대","vendor":"한솥도시락 평택고덕삼성전자점","supply":25909,"vat":2591,"total":28500,"pay":"개인카드","pjt":"p4ph2","note":"메가치킨마요, 치킨마요, 빅치킨마요, 김치참치덮밥"},
    {"date":"2026-06-22","cat":"식대","vendor":"백다방 평택고덕SBC점","supply":12455,"vat":1245,"total":13700,"pay":"개인카드","pjt":"p4ph2","note":"복숭아아이스티x1, 아메리카노(HOT)x1, 카페라떼(ICED)x1, 아메리카노(ICED)x3"},
]

ok = 0
for e in EXPENSES:
    fields = {
        "date":{"stringValue":e["date"]},"cat":{"stringValue":e["cat"]},
        "vendor":{"stringValue":e["vendor"]},"supply":{"integerValue":str(e["supply"])},
        "vat":{"integerValue":str(e["vat"])},"total":{"integerValue":str(e["total"])},
        "pay":{"stringValue":e["pay"]},"pjt":{"stringValue":e["pjt"]},"note":{"stringValue":e["note"]}
    }
    try:
        fs_add(token, PROJECT, "gihoek_expenses", fields)
        print(f"✅ [{ok+1}] {e['date']} {e['vendor']} {e['total']:,}원")
        ok += 1
        time.sleep(0.1)
    except Exception as ex:
        print(f"❌ {e['vendor']} 실패: {ex}")

print(f"\n완료: {ok}/20건")
