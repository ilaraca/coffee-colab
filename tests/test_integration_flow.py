import uuid
import pytest
from fastapi.testclient import TestClient

from app.core.db import SessionLocal
from app.core.tokens import generate_verification_token
from app.main import app
from app.models.mission import Mission, MissionStatus
from app.models.portfolio import PortfolioItem
from app.models.transaction import Transaction

client = TestClient(app)

@pytest.fixture(scope="module")
def shared_db():
    db = SessionLocal()
    yield db
    db.close()

@pytest.fixture(scope="module")
def emails():
    return {
        "business": f"bus_{uuid.uuid4().hex[:8]}@example.com",
        "provider": f"prov_{uuid.uuid4().hex[:8]}@example.com"
    }

def test_full_mission_flow(emails, shared_db):
    b_email = emails["business"]
    p_email = emails["provider"]
    
    # 1. Register Business
    res = client.post("/register", data={
        "name": "Cafe Admin", "email": b_email, 
        "password": "Pass123!", "role": "BUSINESS_ADMIN"
    }, follow_redirects=True)
    assert res.status_code == 200
    
    # Verify & Login Business
    token = generate_verification_token(b_email)
    client.get(f"/verify-email?token={token}")
    res = client.post("/login", data={"email": b_email, "password": "Pass123!"}, follow_redirects=False)
    assert res.status_code == 303
    
    # Create Business Profile
    res = client.post("/business/register_profile", data={
        "name": "Integration Cafe", "category": "Cafe"
    }, follow_redirects=False)
    assert res.status_code == 303
    
    # Create Mission
    res = client.post("/business/missions", data={
        "title": "Design Logo", "description": "Need a nice logo", "credit_value": 150
    }, follow_redirects=False)
    assert res.status_code == 303
    
    shared_db.expire_all()
    mission = shared_db.query(Mission).filter(Mission.title == "Design Logo").first()
    assert mission is not None
    assert mission.status == MissionStatus.OPEN
    mission_id = str(mission.id)
    
    # Logout
    client.get("/logout")
    
    # 2. Register Provider
    client.post("/register", data={
        "name": "Talent User", "email": p_email, 
        "password": "Pass123!", "role": "PROVIDER"
    }, follow_redirects=True)
    token_p = generate_verification_token(p_email)
    client.get(f"/verify-email?token={token_p}")
    client.post("/login", data={"email": p_email, "password": "Pass123!"}, follow_redirects=False)
    
    # Accept Mission
    res = client.post(f"/provider/missions/{mission_id}/accept", follow_redirects=False)
    assert res.status_code == 303
    
    shared_db.expire_all()
    mission = shared_db.query(Mission).filter(Mission.id == mission.id).first()
    assert mission.status == MissionStatus.ACCEPTED
    assert mission.accepted_at is not None
    
    # Finish Mission
    res = client.post(f"/provider/missions/{mission_id}/done", data={"proof_of_work": "https://example.com/logo"}, follow_redirects=False)
    assert res.status_code == 303
    
    shared_db.expire_all()
    mission = shared_db.query(Mission).filter(Mission.id == mission.id).first()
    assert mission.status == MissionStatus.DONE
    assert mission.proof_of_work == "https://example.com/logo"
    assert mission.completed_at is not None
    
    # Logout
    client.get("/logout")
    
    # 3. Login Business & Approve
    client.post("/login", data={"email": b_email, "password": "Pass123!"}, follow_redirects=False)
    res = client.post(f"/business/missions/{mission_id}/approve", data={
        "score": 5, "recommendation_text": "Awesome job!", "allow_public": "true"
    }, follow_redirects=False)
    assert res.status_code == 303
    
    shared_db.expire_all()
    mission = shared_db.query(Mission).filter(Mission.id == mission.id).first()
    assert mission.status == MissionStatus.APPROVED
    assert mission.approved_at is not None
    
    # Check Portfolio
    portfolio_item = shared_db.query(PortfolioItem).filter(PortfolioItem.mission_id == mission.id).first()
    assert portfolio_item is not None
    assert portfolio_item.summary == "Awesome job!"
    assert portfolio_item.is_public is True
    
    # Check Wallet Transaction
    tx = shared_db.query(Transaction).filter(Transaction.mission_id == mission.id).first()
    assert tx is not None
    assert tx.amount == 150
    assert tx.type.value == "EARN"
    assert tx.to_user_id == mission.provider_id
    assert tx.from_business_id == mission.business_id
