import json, time, base64, urllib.request, urllib.parse, os
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

SA = json.loads(os.environ["SA_JSON"])

def b64url(data):
    if isinstance(data, str): data = data.encode()
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()

def get_token(sa):
    now = int(time.time())
    header = b64url(json.dumps({"alg":"RS256","typ":"JWT"}))
    payload = b64url(json.dumps({
        "iss": sa["client_email"], "sub": sa["client_email"],
        "aud": "https://oauth2.googleapis.com/token",
        "iat": now, "exp": now + 3600,
        "scope": "https://www.googleapis.com/auth/datastore"
    }))
    msg = f"{header}.{payload}".encode()
    key = serialization.load_pem_private_key(sa["private_key"].encode(), password=None)
    sig = key.sign(msg, padding.PKCS1v15(), hashes.SHA256())
    jwt = f"{header}.{payload}.{b64url(sig)}"
    data = urllib.parse.urlencode({"grant_type":"urn:ietf:params:oauth:grant-type:jwt-bearer","assertion":jwt}).encode()
    with urllib.request.urlopen(urllib.request.Request("https://oauth2.googleapis.com/token", data=data)) as r:
        return json.loads(r.read())["access_token"]

def fs_set(token, project, col, doc_id, fields):
    url = f"https://firestore.googleapis.com/v1/projects/{project}/databases/(default)/documents/{col}/{doc_id}"
    body = json.dumps({"fields": fields}).encode()
    req = urllib.request.Request(url, data=body, method="PATCH",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

token = get_token(SA)
PROJECT = "p4ph2-fab-506a7"

# 20건 데이터
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

ok, fail = 0, []
for e in EXPENSES:
    doc_id = f"exp_{int(time.time()*1000)}_{ok}"
    time.sleep(0.05)
    fields = {
        "date": {"stringValue": e["date"]},
        "cat":  {"stringValue": e["cat"]},
        "vendor": {"stringValue": e["vendor"]},
        "supply": {"integerValue": str(e["supply"])},
        "vat":    {"integerValue": str(e["vat"])},
        "total":  {"integerValue": str(e["total"])},
        "pay":    {"stringValue": e["pay"]},
        "pjt":    {"stringValue": e["pjt"]},
        "note":   {"stringValue": e["note"]},
    }
    try:
        fs_set(token, PROJECT, "gihoek_expenses", doc_id, fields)
        print(f"✅ [{ok+1}] {e['date']} {e['vendor']} {e['total']:,}원")
        ok += 1
    except Exception as ex:
        print(f"❌ [{ok+1}] {e['vendor']} 실패: {ex}")
        fail.append(e["vendor"])

print(f"\n완료: {ok}건 성공 / {len(fail)}건 실패")
if fail: print("실패:", fail)
