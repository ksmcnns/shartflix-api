from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from database import get_db, BlacklistedToken
from models.user import User
from schemas.user import UserCreate, UserResponse, UserLogin
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt  # Changed from 'jose' to 'jwt'
import os

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/login")

# JWT Config
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    # PyJWT's encode method
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire, "type": "refresh"})
    # PyJWT's encode method
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str, credentials_exception, db):
    try:
        # PyJWT's decode method
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_str = token
        if payload.get("type") == "refresh":
            raise credentials_exception
        if db.query(BlacklistedToken).filter(BlacklistedToken.token == token_str).first():
            raise credentials_exception
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except jwt.PyJWTError: # Changed exception type to PyJWTError
        raise credentials_exception

async def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return verify_token(token, credentials_exception, db)

@router.post("/user/register", response_model=UserResponse)
def register(user: UserCreate, db=Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, email=user.email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/user/login")
def login(user: UserLogin, db=Depends(get_db)):
    print(f"Received login request: {user.dict()}")
    user_db = db.query(User).filter(User.email == user.username).first()
    if not user_db:
        print("User not found")
    elif not pwd_context.verify(user.password, user_db.password):
        print("Password verification failed")
    if not user_db or not pwd_context.verify(user.password, user_db.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user_db.email})
    refresh_token = create_refresh_token(data={"sub": user_db.email})
    print(f"Returning tokens: access_token={access_token}, refresh_token={refresh_token}")
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/user/refresh")
def refresh_token(refresh_token: str, db=Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # PyJWT's decode method
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None or payload.get("type") != "refresh":
            raise credentials_exception
        if db.query(BlacklistedToken).filter(BlacklistedToken.token == refresh_token).first():
            raise credentials_exception
        access_token = create_access_token(data={"sub": username})
        return {"access_token": access_token, "token_type": "bearer"}
    except jwt.PyJWTError: # Changed exception type to PyJWTError
        raise credentials_exception

@router.post("/user/logout")
def logout(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    db_blacklist = BlacklistedToken(token=token)
    db.add(db_blacklist)
    db.commit()
    return {"message": "Logged out successfully"}

@router.get("/user/profile", response_model=UserResponse)
def get_profile(current_user: str = Depends(get_current_user), db=Depends(get_db)):
    user = db.query(User).filter(User.username == current_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/user/upload_photo")
def upload_photo(photo_url: str, current_user: str = Depends(get_current_user), db=Depends(get_db)):
    user = db.query(User).filter(User.username == current_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.photo_url = photo_url
    db.commit()
    return {"message": "Photo uploaded"}