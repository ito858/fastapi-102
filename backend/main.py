from fastapi import FastAPI, Form, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db, Base, engine
from models import User
from auth import hash_password, verify_password, create_access_token, verify_token

app = FastAPI()
Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

@app.post("/api/register")
async def register(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    hashed_password = hash_password(password)
    new_user = User(username=username, password=hashed_password)
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully"}

@app.post("/api/login")
async def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/api/dashboard")
async def dashboard(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = verify_token(token, db)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.query(User).filter(User.username == username).first()
    return {"username": user.username, "message": "Welcome to your dashboard"}

@app.post("/api/logout")
async def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = verify_token(token, db)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    # Add token to blacklist
    blacklisted = BlacklistedToken(token=token)
    db.add(blacklisted)
    db.commit()
    return {"message": "Logged out successfully"}
