from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import get_settings

settings = get_settings

# JWT / auth config
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a plain password against its hashed version."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password for storing."""
    return pwd_context.hash(password)


def create_access_token(subject: str, expires_delta: Optional[int] = None) -> str:
    """
    Create a JWT access token.

    `subject` will typically be the user's email.
    `expires_delta` is in minutes; if None, read from settings or use default (60).
    """
    minutes = expires_delta or getattr(
        settings,
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    expire = datetime.utcnow() + timedelta(minutes=minutes)
    to_encode = {"sub": subject, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """
    Decode a JWT token and return the payload.

    Raises HTTP 401 if token is invalid or expired.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        # invalid signature, expired, malformed, etc.
        raise credentials_exception
