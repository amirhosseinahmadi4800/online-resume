from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# =======================
# تنظیمات امنیتی
# =======================

SECRET_KEY = "SUPER_SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# =======================
# ادمین ثابت (برای پروژه درسی)
# =======================

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# =======================
# هش پسورد ادمین (lazy init)
# =======================

ADMIN_HASHED_PASSWORD = None

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def get_admin_hashed_password() -> str:
    global ADMIN_HASHED_PASSWORD
    if ADMIN_HASHED_PASSWORD is None:
        ADMIN_HASHED_PASSWORD = get_password_hash(ADMIN_PASSWORD)
    return ADMIN_HASHED_PASSWORD

# =======================
# احراز هویت
# =======================

def authenticate_user(username: str, password: str):
    if username != ADMIN_USERNAME:
        return False

    if not verify_password(password, get_admin_hashed_password()):
        return False

    return {"username": username}

# =======================
# JWT
# =======================

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_admin(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")

        if username != ADMIN_USERNAME:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authorized"
            )

        return username

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
