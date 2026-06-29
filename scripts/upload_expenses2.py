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
    {"date":"2026-06-22","cat":"기타","vendor":"(주)가비아","supply":15000,"vat":1500,"total":16500,"pay":"개인카드","pjt":"p4ph2","note":"도메인 서비스 신규"},
    {"date":"2026-06-22","cat":"식대","vendor":"이마트24 고덕SBC점","supply":2727,"vat":273,"total":3000,"pay":"개인카드","pjt":"p4ph2","note":"광동진한맛개차펫500mlx2"},
    {"date":"2026-06-23","cat":"기타","vendor":"한국도로교통공단 용인운전면허시험장","supply":4000,"vat":0,"total":4000,"pay":"개인카드","pjt":"p4ph2","note":"수수료"},
    {"date":"2026-06-23","cat":"기타","vendor":"한국도로교통공단 용인운전면허시험장","supply":30000,"vat":0,"total":30000,"pay":"개인카드","pjt":"p4ph2","note":"수수료"},
    {"date":"2026-06-23","cat":"사무용품","vendor":"다이소 평택장당점","supply":11817,"vat":1183,"total":13000,"pay":"개인카드","pjt":"p4ph2","note":"정부환일, 두인쇄홀더, 클리어파일리필, 마우스패드, 오피스테이블정리대 등"},
    {"date":"2026-06-24","cat":"식대","vendor":"백다방 평택고덕SBC점","supply":10000,"vat":1000,"total":11000,"pay":"개인카드","pjt":"p4ph2","note":"아메리카노x2, 백사이즈복숭아아이스티x1, 레몬얼그레이티x1"},
    {"date":"2026-06-24","cat":"식대","vendor":"태청위도유 고덕점","supply":35456,"vat":3544,"total":39000,"pay":"개인카드","pjt":"p4ph2","note":"뼈해장국, 특)뼈해장국, 내장탕"},
    {"date":"2026-06-24","cat":"공구·자재비","vendor":"부연상사","supply":68182,"vat":6818,"total":75000,"pay":"개인카드","pjt":"p4ph2","note":"무초산실리콘/신에츠 x25"},
    {"date":"2026-06-23","cat":"식대","vendor":"79네수육국밥 고덕점","supply":31818,"vat":3182,"total":35000,"pay":"개인카드","pjt":"p4ph2","note":"순대국밥(특)x1, 수육국밥x2"},
    {"date":"2026-06-24","cat":"공구·자재비","vendor":"부연상사","supply":9545,"vat":955,"total":10500,"pay":"개인카드","pjt":"p4ph2","note":"상품(3,500x3)"},
    {"date":"2026-06-23","cat":"식대","vendor":"GS25 고덕원희캐슬점","supply":2728,"vat":272,"total":3000,"pay":"개인카드","pjt":"p4ph2","note":"CLOOP제로복숭아x1, CLOOP제로포도x1"},
    {"date":"2026-06-25","cat":"식대","vendor":"세븐일레븐 평택고덕산업단지점","supply":19909,"vat":1991,"total":21900,"pay":"개인카드","pjt":"p4ph2","note":"컵라면, 김밥, 음료 등"},
    {"date":"2026-06-27","cat":"식대","vendor":"태청위도유 고덕점","supply":25456,"vat":2544,"total":28000,"pay":"개인카드","pjt":"p4ph2","note":"특)뼈해장국x1, 내장탕x1"},
    {"date":"2026-06-26","cat":"식대","vendor":"황철수피자 고덕점","supply":64546,"vat":6454,"total":71000,"pay":"개인카드","pjt":"p4ph2","note":"황철수스페셜대x1, 불고기치즈바이트피자대x1, 코카콜라제로1.25L"},
    {"date":"2026-06-29","cat":"공구·자재비","vendor":"넘버원상사(주)평택","supply":135000,"vat":13500,"total":148500,"pay":"현금","pjt":"p4ph2","note":"파이프안전커버(황.곱)1롤50개x2M x50"},
    {"date":"2026-06-26","cat":"공구·자재비","vendor":"거상주식회사","supply":26000,"vat":2600,"total":28600,"pay":"현금","pjt":"p4ph2","note":"실리콘건(핫터건/헤라포함)x4, 드라이버x1"},
    {"date":"2026-06-24","cat":"공구·자재비","vendor":"거상주식회사","supply":49000,"vat":4900,"total":53900,"pay":"현금","pjt":"p4ph2","note":"장갑(3M)슈퍼그립200(L)x10, 내화학장갑x1"},
    {"date":"2026-06-16","cat":"공구·자재비","vendor":"넘버원상사(주)평택","supply":48800,"vat":4880,"total":53680,"pay":"현금","pjt":"p4ph2","note":"가축제안전화PRO6-100Y, 제전가방x2, 기술인조끼"},
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

print(f"\n완료: {ok}/18건")
