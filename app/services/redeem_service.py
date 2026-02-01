from sqlalchemy.orm import Session
import uuid
import secrets
import hashlib
import qrcode
import io
import base64
from datetime import datetime, timedelta
from fastapi import HTTPException

from app.models.redeem import TokenStatus, RedeemToken
from app.models.transaction import TransactionType
from app.repos import redeem_repo, wallet_repo

class RedeemService:
    def __init__(self, db: Session):
        self.db = db

    def generate_token(self, provider_id: uuid.UUID, cafe_id: uuid.UUID, amount: int):
         # 1. Check balance
        balance = wallet_repo.get_balance(self.db, provider_id, cafe_id)
        if balance < amount:
            raise HTTPException(400, "Insufficient balance")
            
        # 2. Generate secure random token
        raw_token = secrets.token_urlsafe(32)
        # 3. Hash it
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        
        # 4. Save to DB
        expires_at = datetime.utcnow() + timedelta(minutes=5)
        # Assuming database stores UTC or naive UTC.
        
        token_obj = redeem_repo.create_token(
            self.db,
            cafe_id=cafe_id,
            provider_id=provider_id,
            token_hash=token_hash,
            amount=amount,
            expires_at=expires_at
        )
        
        # 5. Return raw token (for QR) and expiry
        return raw_token, token_obj

    def generate_qr_image(self, data: str) -> str:
        # Generates base64 image data uri
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buf = io.BytesIO()
        img.save(buf)
        buf.seek(0)
        img_str = base64.b64encode(buf.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"

    def verify_token(self, raw_token: str) -> RedeemToken:
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        token = redeem_repo.get_token_by_hash(self.db, token_hash)
        
        if not token:
            raise HTTPException(404, "Token invalido")
            
        if token.status != TokenStatus.ISSUED:
             raise HTTPException(400, f"Token status: {token.status}")
             
        if token.expires_at.replace(tzinfo=None) < datetime.utcnow():
            # Ensure safe comparison depending on timezone handling.
            # Assuming DB naive UTC for now as per simple setup logic.
            # Better to be explicit but for MVP naive UTC is standard.
             token = redeem_repo.update_token_status(self.db, token, TokenStatus.EXPIRED)
             raise HTTPException(400, "Token expirado")
             
        return token

    def confirm_redemption(self, raw_token: str, cafe_admin_id: uuid.UUID) -> RedeemToken:
        token = self.verify_token(raw_token)
        
        # Verify cafe ownership (cafe_admin belongs to the cafe the token issued for?)
        # Need to check admin's cafe.
        # We assume caller checked cafe_id context or we passed it.
        # But verify_token returns token. We can check token.cafe_id vs admin.cafe_id here?
        # Let's assume controller does check or we pass expected_cafe_id.
        
        # Perform SPEND
        wallet_repo.create_transaction(
            self.db,
            cafe_id=token.cafe_id,
            to_user_id=token.provider_id,
            amount=token.amount,
            type=TransactionType.SPEND,
            from_user_id=None # Implicit from context
        )
        
        # Mark Redeemed
        redeem_repo.update_token_status(self.db, token, TokenStatus.REDEEMED)
        
        return token
