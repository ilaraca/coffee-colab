from app.core.db import SessionLocal
from app.models.transaction import Transaction
from app.models.user import User

db = SessionLocal()

# 1. Fetch Provider
provider = db.query(User).filter(User.email == "provider@modocafe.local").first()
print(f"Provider: {provider.name} (ID: {provider.id})")

# 2. Fetch Transactions
txs = db.query(Transaction).filter(Transaction.to_user_id == provider.id).all()
print(f"Found {len(txs)} transactions for provider.")

for tx in txs:
    print(f"Tx: {tx.id} | Type: {tx.type} | Amount: {tx.amount} | Status: {tx.status}")

db.close()
