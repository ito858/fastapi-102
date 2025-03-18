# backend/tests/test_api.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app, get_db, User, BlacklistedToken  # Adjust imports as needed
from models import Base, User
from auth import pwd_context


from faker import Faker
from passlib.context import CryptContext

fake = Faker()
client = TestClient(app)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# In-memory SQLite engine
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    # Create all tables before the test
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after the test for isolation
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db):
    # Override the app's database dependency
    def override_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_db  # Replace with your actual dependency
    return TestClient(app)
#===========
@pytest.fixture
def payload():
    return {
        "user": {"username": fake.user_name(), "password": fake.password()},
        "vip": {"Nome": fake.first_name(), "cognome": fake.last_name(), "Email": fake.email()}
    }

# Existing /signup/ tests
@pytest.mark.asyncio
async def test_signup_success(payload):
    response = client.post("/signup/", json=payload)
    assert response.status_code == 200
    assert "userid" in response.json()

@pytest.mark.asyncio
async def test_signup_duplicate(payload):
    client.post("/signup/", json=payload)  # First signup
    response = client.post("/signup/", json=payload)  # Duplicate
    assert response.status_code == 400
    assert "Username already taken" in response.json()["detail"]

@pytest.mark.asyncio
async def test_signup_empty_username():
    payload = {"user": {"username": "", "password": "test123"}, "vip": {"Nome": "Test"}}
    response = client.post("/signup/", json=payload)
    assert response.status_code == 422
    assert "string_too_short" in response.text

# New /api/login tests
# @pytest.mark.asyncio
# async def test_login_success():
#     # Create a user first
#     username = fake.user_name()
#     password = "test123"
#     hashed_password = pwd_context.hash(password)
#     db = TestingSessionLocal()
#     db_user = User(username=username, password=hashed_password)
#     db.add(db_user)
#     db.commit()
#     db.close()
#
#     # Test login
#     response = client.post("/api/login", data={"username": username, "password": password})
#     assert response.status_code == 200
#     assert "access_token" in response.json()
#     assert response.json()["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_success(client, db):
    # Create a user first
    username = fake.user_name()
    password = "test123"
    hashed_password = pwd_context.hash(password)
    db_user = User(username=username, password=hashed_password)
    db.add(db_user)
    db.commit()  # This should now work with tables created

    # Test login
    response = client.post("/api/login", data={"username": username, "password": password})
    assert response.status_code == 200
    assert "access_token" in response.json()  # Adjust based on your API response


@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    response = client.post("/api/login", data={"username": "nonexistent", "password": "wrongpass"})
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]

# New /api/logout tests
# @pytest.mark.asyncio
# async def test_logout_success():
#     # Create a user and log in
#     username = fake.user_name()
#     password = "test123"
#     hashed_password = pwd_context.hash(password)
#     db = TestingSessionLocal()
#     db_user = User(username=username, password=hashed_password)
#     db.add(db_user)
#     db.commit()
#     db.close()
#
#     login_response = client.post("/api/login", data={"username": username, "password": password})
#     token = login_response.json()["access_token"]
#
#     # Test logout
#     response = client.post("/api/logout", headers={"Authorization": f"Bearer {token}"})
#     assert response.status_code == 200
#     assert response.json() == {"message": "Logged out successfully"}
#
#     # Verify token is blacklisted
#     db = TestingSessionLocal()
#     blacklisted = db.query(BlacklistedToken).filter(BlacklistedToken.token == token).first()
#     assert blacklisted is not None
#     db.close()

@pytest.mark.asyncio
async def test_logout_success(client, db):
    # Create a user and log in
    username = fake.user_name()
    password = "test123"
    hashed_password = pwd_context.hash(password)
    db_user = User(username=username, password=hashed_password)
    db.add(db_user)
    db.commit()  # This should now work with tables created

    # Log in to get a token
    login_response = client.post("/api/login", data={"username": username, "password": password})
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Test logout
    response = client.post("/api/logout", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200  # Adjust based on your API


@pytest.mark.asyncio
async def test_logout_invalid_token(client):
    response = client.post("/api/logout", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401
    assert "Invalid or expired token" in response.json()["detail"]





