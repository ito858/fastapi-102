from fastapi import FastAPI, Form, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import StreamingResponse  # Add this import
from sqlalchemy.orm import Session
from auth import hash_password, verify_password, create_access_token, verify_token
import barcode  # This should work if python-barcode is installed
from barcode.writer import ImageWriter
from io import BytesIO

from database import get_db, Base, engine
from models import *


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

@app.post("/signup/")
async def signup(user: UserCreate, vip: VIP, db: Session = Depends(get_db)):
    # Create user
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    hashed_password = hash_password(user.password)
    db_user = User(username=user.username, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)


    # Create VIP with IDvip = userid
#     vip_data = vip.dict()  # Convert Pydantic model to dict
    vip_data = vip.model_dump()   # Convert Pydantic model to dict
    vip_data["IDvip"] = db_user.id  # Add IDvip to the dict
    db_vip = VIPTable(**vip_data)  # Pass the updated dict to SQLAlchemy
    db.add(db_vip)
    db.commit()
    return {"message": "User and VIP registered", "userid": db_user.id}


@app.post("/api/login")
async def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": username})
    return {"access_token": token, "token_type": "bearer"}

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

# New endpoint to generate barcode
@app.get("/api/barcode")
async def get_barcode(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Verify the token and get the username
    username = verify_token(token, db)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # Fetch the user and their VIP data
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    vip = db.query(VIPTable).filter(VIPTable.IDvip == user.id).first()
    if not vip or not vip.code:
        raise HTTPException(status_code=404, detail="VIP membership not found")

    # Generate Code128 barcode
    code128 = barcode.get_barcode_class('code128')
    barcode_instance = code128(vip.code, writer=ImageWriter())

    # Save barcode to a BytesIO buffer (in-memory)
    buffer = BytesIO()
    barcode_instance.write(buffer)
    buffer.seek(0)

    # Return the image as a streaming response
    return StreamingResponse(buffer, media_type="image/png", headers={"Content-Disposition": f"inline; filename={vip.code}.png"})


# @app.get("/api/dashboard")
# async def dashboard(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     username = verify_token(token, db)
#     if not username:
#         raise HTTPException(status_code=401, detail="Invalid or expired token")
#     user = db.query(User).filter(User.username == username).first()
#     return {"username": user.username, "message": "Welcome to your dashboard"}
# upgraded version of dashboard
@app.get("/api/dashboard")
async def dashboard(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = verify_token(token, db)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # Fetch user and VIP data
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    vip = db.query(VIPTable).filter(VIPTable.IDvip == user.id).first()
    if not vip:
        raise HTTPException(status_code=404, detail="VIP data not found")

    # Construct response with all relevant data
    response = {
        "username": user.username,
        "vip": {
            "IDvip": vip.IDvip,
            "code": vip.code,
            "nascita": vip.nascita,
            "cellulare": vip.cellulare,
            "sms": vip.sms,
            "Punti": vip.Punti,
            "Sconto": vip.Sconto,
            "Ck": vip.Ck,
            "idata": vip.idata.isoformat() if vip.idata else None,
            "ioperatore": vip.ioperatore,
            "inegozio": vip.inegozio,
            "P_cs": vip.P_cs,
            "P_ldata": vip.P_ldata,
            "P_importo": float(vip.P_importo) if vip.P_importo is not None else 0.00,  # Convert Decimal to float
            "Nome": vip.Nome,
            "Indirizzo": vip.Indirizzo,
            "Cap": vip.Cap,
            "Citta": vip.Citta,
            "Prov": vip.Prov,
            "CodiceFiscale": vip.CodiceFiscale,
            "PartitaIva": vip.PartitaIva,
            "Email": vip.Email,
            "sesso": vip.sesso,
            "VIPanno": vip.VIPanno,
            "maps": vip.maps,
            "VIPscadenza": vip.VIPscadenza,
            "Blocco": vip.Blocco,
            "cognome": vip.cognome,
            "SerBlocco": vip.SerBlocco,
            "SerBloccoBz": vip.SerBloccoBz,
            "omail": vip.omail,
            "oposte": vip.oposte,
            "msg": vip.msg,
            "msgstr": vip.msgstr,
            "utime": vip.utime,
            "upc": vip.upc,
            "uzt": vip.uzt,
            "un": vip.un,
            "lotteria": vip.lotteria,
            "statoanno": vip.statoanno,
            "img": vip.img.hex() if vip.img else None,  # Convert bytes to hex string
            "n": vip.n,
            "SCOscadenza": vip.SCOscadenza,
        }
    }
    return response
