"""
portal_users 컬렉션에서 admin 필드를 정리하는 스크립트.
지정된 4명(김종화·김영희·김민서·송지훈)만 admin:true로 남기고, 나머지 전 계정은 admin:false로 맞춘다.
admin 필드 외 다른 필드(perms, status, name 등)는 건드리지 않는다.

실행 방법 (김짜장님 로컬 PC에서):
1. 서비스 계정 키 파일을 이 스크립트와 같은 폴더에 둔다
   - 본섭: p4ph2-fab-506a7-firebase-adminsdk-fbsvc-f84b0371ec.json
   - 테섭: portal-test-6e0ff-firebase-adminsdk-fbsvc-fd25dd577d.json
2. pip install firebase-admin  (최초 1회)
3. python set_admin_accounts.py p4ph2-fab-506a7-firebase-adminsdk-fbsvc-f84b0371ec.json   ← 본섭 적용
4. python set_admin_accounts.py portal-test-6e0ff-firebase-adminsdk-fbsvc-fd25dd577d.json ← 테섭 적용
   (둘 다 적용하려면 두 번 실행)

실제로 반영하기 전, 먼저 --dry-run으로 무엇이 바뀌는지 미리 확인할 수 있다:
   python set_admin_accounts.py <키파일.json> --dry-run
"""
import sys
import firebase_admin
from firebase_admin import credentials, firestore

# ── 관리자로 지정할 4명 ──
ADMIN_EMAILS = {
    "jh.kim@jhsol.kr",   # 김종화
    "yh.kim@jhsol.kr",   # 김영희
    "ms.kim@jhsol.kr",   # 김민서
    "ceo@jhsol.kr",      # 송지훈
}

def main():
    if len(sys.argv) < 2:
        print("사용법: python set_admin_accounts.py <서비스계정키.json> [--dry-run]")
        sys.exit(1)
    key_path = sys.argv[1]
    dry_run = "--dry-run" in sys.argv

    cred = credentials.Certificate(key_path)
    firebase_admin.initialize_app(cred, name=key_path)  # 여러 프로젝트 연속 실행 대비 앱 이름 분리
    db = firestore.client(firebase_admin.get_app(key_path))

    docs = list(db.collection("portal_users").stream())
    print(f"=== portal_users 총 {len(docs)}건 확인 ===\n")

    to_grant, to_revoke, unchanged, not_found_emails = [], [], [], set(ADMIN_EMAILS)

    for d in docs:
        data = d.to_dict()
        email = (data.get("email") or "").strip().lower()
        name = data.get("name", "-")
        cur_admin = bool(data.get("admin", False))
        should_be_admin = email in ADMIN_EMAILS

        if should_be_admin:
            not_found_emails.discard(email)

        if should_be_admin and not cur_admin:
            to_grant.append((d.id, name, email))
        elif not should_be_admin and cur_admin:
            to_revoke.append((d.id, name, email))
        else:
            unchanged.append((d.id, name, email, cur_admin))

    print(f"[관리자로 새로 지정] {len(to_grant)}건")
    for uid, name, email in to_grant:
        print(f"  + {name:10s} {email}")

    print(f"\n[관리자 권한 해제] {len(to_revoke)}건")
    for uid, name, email in to_revoke:
        print(f"  - {name:10s} {email}")

    print(f"\n[변경 없음] {len(unchanged)}건 (그대로 유지)")

    if not_found_emails:
        print(f"\n⚠️ portal_users에 아직 계정이 없는 이메일 (한 번도 로그인 안 함): {', '.join(sorted(not_found_emails))}")
        print("   → 해당 계정은 최초 로그인 후 이 스크립트를 다시 실행해야 admin:true가 반영됩니다.")

    if dry_run:
        print("\n(--dry-run 이라 실제로 저장하지 않았습니다. 결과가 맞으면 --dry-run 없이 다시 실행하세요.)")
        return

    for uid, name, email in to_grant:
        db.collection("portal_users").document(uid).update({"admin": True})
    for uid, name, email in to_revoke:
        db.collection("portal_users").document(uid).update({"admin": False})

    print(f"\n✅ 완료: {len(to_grant)}건 관리자 지정, {len(to_revoke)}건 관리자 해제")

if __name__ == "__main__":
    main()
