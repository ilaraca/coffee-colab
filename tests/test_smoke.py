from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_main():
    """
    Smoke test: Checks if the main endpoint returns 200.
    Since we redirect logged-in users or showing landing page, we expect either 200 or 307 (redirect) depending on state,
    but for a fresh unauthed client it should be 200 (landing page).
    """
    response = client.get("/")
    assert response.status_code == 200
    assert "Seu Talento Vale Café" in response.text
