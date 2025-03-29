from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
import os

# Load secret key from .env
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")  # Use the one you generated!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """ Hash a password using bcrypt """
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password) -> bool:
    """ Verify a password against its hashed version """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """ Generate a JWT token """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict | None:
    """ Decode and verify a JWT token """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
