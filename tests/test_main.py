from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_shorten_url():
    response = client.post("/shorten", json={"original_url": "https://example.com"})
    assert response.status_code == 200
    assert "short_url" in response.json()
