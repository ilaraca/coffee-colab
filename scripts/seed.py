import asyncio
import sys
import os

# Add parent directory to path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.core.db import SessionLocal, engine, Base
from app.models.cafe import Cafe
from app.models.user import User, UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed():
    db = SessionLocal()
    try:
        # Check if Admin already exists (more robust than checking Cafe)
        if db.query(User).filter_by(email="admin@modocafe.local").first():
            print("Already seeded (based on Admin user).")
            return

        print("Seeding...")
        
        # 1. Cafe (Get or Create)
        cafe = db.query(Cafe).filter_by(slug="modo-cafe").first()
        if not cafe:
            cafe = Cafe(name="Modo Café", slug="modo-cafe")
            db.add(cafe)
            db.commit()
            db.refresh(cafe)
            print(f"Created Cafe: {cafe.name}")
        else:
            print(f"Cafe found: {cafe.name}")

        # 2. Admin
        admin_pass = pwd_context.hash("Admin123!")
        admin = User(
            cafe_id=cafe.id,
            name="Cafe Admin",
            email="admin@modocafe.local",
            password_hash=admin_pass,
            role=UserRole.CAFE_ADMIN
        )
        db.add(admin)
        print(f"Created Admin: {admin.email}")

        # 3. Provider
        provider_pass = pwd_context.hash("Provider123!")
        provider = User(
            cafe_id=None, #/Global? Or specific? Prompt said "1 provider". Let's link to cafe for MVP context if needed, but schema allows null.
            name="John Provider",
            email="provider@modocafe.local",
            password_hash=provider_pass,
            role=UserRole.PROVIDER
        )
        # Note: If provider needs to interact with cafe, they just accept missions. 
        # But for 'transactions', we need a provider.
        db.add(provider)
        print(f"Created Provider: {provider.email}")
        
        db.commit()
        print("Seeding complete.")
        
    except Exception as e:
        print(f"Error seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
