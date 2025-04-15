from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.database import get_user_api_db
from app.models.user import AdminUser
from app.schemas.user import AdminUserCreate, AdminUserResponse, LoginRequest
from app.utils.security import hash_password, verify_password, create_access_token  
from datetime import timedelta

router = APIRouter()

@router.post("/register", response_model=AdminUserResponse)
def register(user: AdminUserCreate, db: Session = Depends(get_user_api_db)):
    """ Register a new admin user """
    
    print(f"Checking for existing user with email: {user.email}") 
    existing_user = db.query(AdminUser).filter(AdminUser.email == user.email).first()
    
    if existing_user:
        print(f"User found: {existing_user}")  # Debug log
        raise HTTPException(status_code=400, detail="Email already registered")  

    print("No existing user found. Creating new user...")  # Debug log
    new_user = AdminUser(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password) 
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    #db.close()
    
    print("User registered successfully:", new_user)  # Debug log
    return new_user



@router.post("/login")
def login(user: LoginRequest, db: Session = Depends(get_user_api_db)):
    """ Authenticate users and generate a JWT token """

    db_user = db.query(AdminUser).filter(AdminUser.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="User not found")

    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": db_user.email}, expires_delta=timedelta(minutes=30))
    
    return {"access_token": access_token, "token_type": "bearer"}
