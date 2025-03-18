# backend/tests/test_api.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from main import app  # Replace with your actual app module
from auth import pwd_context  # Replace with your actual auth module
from database import get_db  # Replace with your actual dependency module
from faker import Faker

fake = Faker()

# Define models inline for clarity (move to your_app/models.py in practice)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, nullable=False)

# Global in-memory SQLite engine
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    # Create all tables before the test
    Base.metadata.create_all(bind=engine)
    print(f"Tables created: {list(Base.metadata.tables.keys())}")
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db):
    # Override the app's database dependency
    app.dependency_overrides[get_db] = lambda: db
    print(f"DB engine in test: {db.bind}")
    return TestClient(app)

@pytest.fixture
def payload():
    return {
        "user": {"username": fake.user_name(), "password": fake.password()},
        "vip": {"Nome": fake.first_name(), "cognome": fake.last_name(), "Email": fake.email()}
    }

# Signup Tests
@pytest.mark.asyncio
async def test_signup_success(client, payload, db):
    response = client.post("/signup/", json=payload)
    assert response.status_code == 200
    assert "userid" in response.json()

@pytest.mark.asyncio
async def test_signup_duplicate(client, payload, db):
    client.post("/signup/", json=payload)
    response = client.post("/signup/", json=payload)
    assert response.status_code == 400
    assert "already exists" in response.json().get("detail", "").lower()

@pytest.mark.asyncio
async def test_signup_empty_username(client, db):
    payload = {
        "user": {"username": "", "password": fake.password()},
        "vip": {"Nome": fake.first_name(), "cognome": fake.last_name(), "Email": fake.email()}
    }
    response = client.post("/signup/", json=payload)
    assert response.status_code == 422
    # Handle FastAPI validation error (list of dicts)
    detail = response.json()["detail"]
    assert isinstance(detail, list)
    assert any("username" in str(d).lower() for d in detail)

# Login Tests
@pytest.mark.asyncio
async def test_login_success(client, db):
    username = fake.user_name()
    password = "test123"
    hashed_password = pwd_context.hash(password)
    db_user = User(username=username, password=hashed_password)
    db.add(db_user)
    db.commit()
    response = client.post("/api/login", data={"username": username, "password": password})
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_login_invalid_credentials(client, db):
    response = client.post("/api/login", data={"username": "nonexistent", "password": "wrongpass"})
    assert response.status_code == 401
    assert "invalid credentials" in response.json()["detail"].lower()

# Logout Tests
@pytest.mark.asyncio
async def test_logout_success(client, db):
    username = fake.user_name()
    password = "test123"
    hashed_password = pwd_context.hash(password)
    db_user = User(username=username, password=hashed_password)
    db.add(db_user)
    db.commit()
    login_response = client.post("/api/login", data={"username": username, "password": password})
    token = login_response.json()["access_token"]
    response = client.post("/api/logout", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_logout_invalid_token(client, db):
    response = client.post("/api/logout", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401
    assert "invalid" in response.json().get("detail", "").lower()
