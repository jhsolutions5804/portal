"""
portal_users 컬렉션에서 admin 필드 상태를 확인하는 진단 스크립트.
김짜장님 로컬 PC에서 실행 (Firebase Admin SDK 키 필요).
"""
import firebase_admin
from firebase_admin import credentials, firestore

# 서비스 계정 키 경로 (다운로드된 위치로 수정)
cred = credentials.Certificate("p4ph2-fab-506a7-firebase-adminsdk-fbsvc-f84b0371ec.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

print("=== portal_users 전체 목록 (admin/edoc 권한 확인) ===\n")
docs = db.collection('portal_users').stream()
for doc in docs:
    d = doc.to_dict()
    name = d.get('name', '-')
    admin = d.get('admin', False)
    status = d.get('status', '-')
    perms = d.get('perms', {})
    edoc_perm = perms.get('edoc', False) if isinstance(perms, dict) else False
    print(f"{name:10s} | uid={doc.id[:8]}... | status={status:10s} | admin={admin} | perms.edoc={edoc_perm}")
