"""
Script tao/reset admin user nhanh.
Chay: python create_admin.py
"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, engine, Base
from app.models.user import User
from app.core.security import get_password_hash

# Dam bao tables ton tai
Base.metadata.create_all(bind=engine)

db = SessionLocal()
try:
    ACCOUNTS = [
        {"email": "admin@vietfood.ai", "password": "admin123", "full_name": "Admin VietFood", "role": "admin"},
        {"email": "user@vietfood.ai",  "password": "user123",  "full_name": "Nguyen Van A",   "role": "user"},
    ]
    for acc in ACCOUNTS:
        existing = db.query(User).filter(User.email == acc["email"]).first()
        if existing:
            existing.hashed_password = get_password_hash(acc["password"])
            existing.is_active = True
            print(f"[OK] Reset: {acc['email']} / {acc['password']}")
        else:
            user = User(
                email=acc["email"],
                hashed_password=get_password_hash(acc["password"]),
                full_name=acc["full_name"],
                role=acc["role"],
                is_active=True,
            )
            db.add(user)
            print(f"[OK] Created: {acc['email']} / {acc['password']}")
    db.commit()
    print("\n=== DONE ===")
    print("Login admin : admin@vietfood.ai  / admin123")
    print("Login user  : user@vietfood.ai   / user123")
except Exception as e:
    db.rollback()
    print(f"\n[ERROR] {e}")
finally:
    db.close()
