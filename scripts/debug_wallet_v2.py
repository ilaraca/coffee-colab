from app.core.db import SessionLocal
from app.models.transaction import Transaction, TransactionType
from app.models.user import User

db = SessionLocal()

# 1. Fetch Provider
provider = db.query(User).filter(User.email == "provider@modocafe.local").first()
print(f"Provider: {provider.name} (ID: {provider.id})")

# 2. Fetch Transactions via Repo Logic
txs = db.query(Transaction).filter(Transaction.to_user_id == provider.id).all()
print(f"Found {len(txs)} transactions for provider.")

balance = 0
for tx in txs:
    print(f"Processing Tx {tx.id}...")
    print(f"  Type (Raw): {tx.type}, Type (Type): {type(tx.type)}")
    try:
        print(f"  Type.value: {tx.type.value}")
    except Exception as e:
        print(f"  Error accessing .value: {e}")

    try:
        if tx.type.value == 'EARN': 
            balance += tx.amount
            print("  Action: +EARN")
        elif tx.type.value == 'SPEND': 
            balance -= tx.amount
            print("  Action: -SPEND")
        else:
            print("  Action: IGNORED")
    except Exception as e:
        print(f"  Loop Error: {e}")

print(f"Final Balance: {balance}")
db.close()
