import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db, URL
from app.main import app

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    if os.path.exists("test.db"):
        os.remove("test.db")

    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

    if os.path.exists("test.db"):
        os.remove("test.db")

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
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
