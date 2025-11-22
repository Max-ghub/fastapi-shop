from datetime import datetime, timezone, timedelta

from passlib.context import CryptContext
from jose import jwt

from app.core.config import settings

SECRET_KEY = settings.jwt_secret
ALGORITHM = settings.jwt_algorithm
TTL = settings.access_token_expire_minutes

pwd_context = CryptContext(
    schemes=["sha256_crypt"],
    deprecated = "auto"
)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password, password_hash) -> bool:
    return pwd_context.verify(plain_password, password_hash)

def create_access_token(user_id: int, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=TTL)
    to_encode = {
        "sub": str(user_id),
        "user_id": user_id,
        "role": role,
        "exp": expire,
    }
    return jwt.encode(claims=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    return jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM])