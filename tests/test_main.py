from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_shorten_url():
    response = client.post("/shorten", json={"original_url": "https://example.com"})
    assert response.status_code == 200
    assert "short_url" in response.json()

def test_redirect_url():
    response = client.post("/shorten", json={"original_url": "https://example.com"})
    assert response.status_code == 200
    short_url = response.json()["short_url"]
    short_id = short_url.rsplit("/", 1)[-1]

    response = client.get(f"/{short_id}")
    assert response.status_code == 307
    assert response.headers["location"] == "https://example.com"

def test_redirect_url_not_found():
    response = client.get("/nonexistent123")
    assert response.status_code == 404
    assert response.json()["detail"] == "URL not found"

def test_custom_alias():
    alias = "custom123"
    response = client.post("/shorten", json={
        "original_url": "https://example.com",
        "custom_alias": alias
    })
    assert response.status_code == 200
    assert response.json()["short_url"].endswith(f"/{alias}")

def test_duplicate_custom_alias():
    alias = "dupe123"
    client.post("/shorten", json={
        "original_url": "https://example.com",
        "custom_alias": alias
    })

    response = client.post("/shorten", json={
        "original_url": "https://example.com",
        "custom_alias": alias
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "ID already in use"

def test_missing_original_url():
    response = client.post("/shorten", json={})
    assert response.status_code == 422
