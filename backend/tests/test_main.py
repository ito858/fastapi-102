# backend/tests/test_api.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from main import app
from database import SessionLocal, Base, engine
from models import User, BlacklistedToken
from auth import hash_password, create_access_token


# Define the client as a pytest fixture
@pytest.fixture(scope="function")
def client():
    return TestClient(app)



# Fixture for database session
@pytest.fixture(scope="function")
def db():
    # Create the database tables
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Clean up after each test
        Base.metadata.drop_all(bind=engine)

@pytest.mark.asyncio
async def test_login_success(client, db):
    # Create test user
    username = "testuser"
    password = "test123"
    hashed_password = hash_password(password)  # Use the auth module's hash_password
    db_user = User(username=username, password=hashed_password)
    db.add(db_user)
    db.commit()

    # Test login
    response = client.post("/api/login", data={"username": username, "password": password})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_invalid_credentials(client, db):
    # Test login with non-existent credentials
    response = client.post("/api/login", data={"username": "nonexistent", "password": "wrongpass"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

@pytest.mark.asyncio
async def test_logout_success(client, db):
    # Create test user
    username = "testuser"
    password = "test123"
    hashed_password = hash_password(password)
    db_user = User(username=username, password=hashed_password)
    db.add(db_user)
    db.commit()

    # Get token
    login_response = client.post("/api/login", data={"username": username, "password": password})
    token = login_response.json()["access_token"]

    # Test logout
    response = client.post("/api/logout", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["message"] == "Logged out successfully"

    # Verify token is blacklisted
    blacklisted = db.query(BlacklistedToken).filter(BlacklistedToken.token == token).first()
    assert blacklisted is not None

@pytest.mark.asyncio
async def test_logout_invalid_token(client, db):
    # Test logout with invalid token
    response = client.post("/api/logout", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"
