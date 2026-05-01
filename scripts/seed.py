import asyncio
import sys
import os

# Add parent directory to path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.core.db import SessionLocal, engine, Base
from app.models.business import Business
from app.models.user import User, UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed():
    db = SessionLocal()
    try:
        # Check if Admin already exists (more robust than checking Business)
        if db.query(User).filter_by(email="admin@modocolab.local").first():
            print("Already seeded (based on Admin user).")
            return

        print("Seeding...")
        
        # 1. Business (Get or Create)
        business = db.query(Business).filter_by(slug="modo-colab").first()
        if not business:
            business = Business(
                name="Modo Colab", 
                slug="modo-colab",
                category="Coworking / Café",
                website_url="https://modocolab.com.br",
                instagram_url="https://instagram.com/modocolab",
                is_verified=True
            )
            db.add(business)
            db.commit()
            db.refresh(business)
            print(f"Created Business: {business.name}")
        else:
            print(f"Business found: {business.name}")

        # 2. Admin
        admin_pass = pwd_context.hash("Admin123!")
        admin = User(
            business_id=business.id,
            name="Business Admin",
            email="admin@modocolab.local",
            password_hash=admin_pass,
            role=UserRole.BUSINESS_ADMIN,
            email_verified=True
        )
        db.add(admin)
        print(f"Created Admin: {admin.email}")

        # 3. Provider
        provider_pass = pwd_context.hash("Provider123!")
        provider = User(
            business_id=None,
            name="John Provider",
            email="provider@modocolab.local",
            password_hash=provider_pass,
            role=UserRole.PROVIDER,
            email_verified=True
        )
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
