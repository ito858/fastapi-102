from sqlalchemy import Column, Integer, String, DateTime
from database import Base
from datetime import datetime  # Import for default value

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(512), nullable=False, index=True)
    blacklisted_at = Column(DateTime, default=datetime.utcnow)
