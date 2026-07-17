from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm  # <-- NEW IMPORT
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.database.connection import get_db
from app.models.user import User
from app.schemas import UserCreate
from app.auth.jwt_handler import create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- SIGNUP STAYS EXACTLY THE SAME ---
@router.post("/signup")
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(user_data.password)
    new_user = User(email=user_data.email, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User successfully created!", "user_email": new_user.email}

# --- UPDATED LOGIN ROUTE ---
@router.post("/login")
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)): # <-- UPDATED
    # 1. Look for the email (Swagger sends it under the 'username' variable)
    user = db.query(User).filter(User.email == user_credentials.username).first() # <-- UPDATED
    
    if not user:
        raise HTTPException(status_code=403, detail="Invalid Credentials")
        
    if not pwd_context.verify(user_credentials.password, user.password_hash):
        raise HTTPException(status_code=403, detail="Invalid Credentials")
        
    # Create the token using the user's ID
    access_token = create_access_token(data={"user_id": user.id})

    return {"access_token": access_token, "token_type": "bearer"}