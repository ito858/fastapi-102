# load_fake_users.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import Session
from database import SessionLocal, Base, engine
from models import User, VIPTable
from auth import hash_password
import json

# Create database tables if they don't exist
Base.metadata.create_all(bind=engine)

def load_users_to_db(json_file: str):
    # Open a database session
    db: Session = SessionLocal()
    try:
        # Read the JSON file
        with open(json_file, "r") as f:
            users = json.load(f)

        for user_data in users:
            # Check if username already exists
            if db.query(User).filter(User.username == user_data["username"]).first():
                print(f"Skipping {user_data['username']} - already exists")
                continue

            # Create User
            hashed_password = hash_password(user_data["password"])
            db_user = User(username=user_data["username"], password=hashed_password)
            db.add(db_user)
            db.commit()
            db.refresh(db_user)

            # Create corresponding VIP entry
            vip_data = user_data["vip"]
            vip_data["IDvip"] = db_user.id  # Link VIP to user ID
            db_vip = VIPTable(**vip_data)
            db.add(db_vip)
            db.commit()

            print(f"Added user: {user_data['username']} with VIP ID: {db_user.id}")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    load_users_to_db("fake_users.json")
