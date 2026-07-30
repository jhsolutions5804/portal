# -*- coding: utf-8 -*-
"""
zone_layouts 컬렉션 이관 스크립트 (portal-test → 프로덕션)
로컬 PC에서 실행하세요. 필요 준비물:
  1) pip install firebase-admin
  2) 아래 두 서비스 계정 키 파일을 이 스크립트와 같은 폴더에 두기
     - portal-test-6e0ff-firebase-adminsdk-fbsvc-fd25dd577d.json  (읽기 원본, 테섭)
     - p4ph2-fab-506a7-firebase-adminsdk-fbsvc-f84b0371ec.json    (쓰기 대상, 본섭)
"""
import firebase_admin
from firebase_admin import credentials, firestore

SRC_KEY = "portal-test-6e0ff-firebase-adminsdk-fbsvc-fd25dd577d.json"
DST_KEY = "p4ph2-fab-506a7-firebase-adminsdk-fbsvc-f84b0371ec.json"
COLLECTION = "zone_layouts"

def main():
    src_app = firebase_admin.initialize_app(credentials.Certificate(SRC_KEY), name="src")
    dst_app = firebase_admin.initialize_app(credentials.Certificate(DST_KEY), name="dst")
    src_db = firestore.client(src_app)
    dst_db = firestore.client(dst_app)

    docs = list(src_db.collection(COLLECTION).stream())
    print(f"테섭 {COLLECTION}에서 {len(docs)}개 구역 문서 발견")

    for d in docs:
        data = d.to_dict()
        points = data.get("points", {})
        print(f"  - {d.id}: 장비 {len(points)}개 매핑됨 → 본섭에 복사 중...")
        dst_db.collection(COLLECTION).document(d.id).set(data)

    print("완료! 본섭 zone_layouts 컬렉션을 확인해보세요.")

if __name__ == "__main__":
    main()
