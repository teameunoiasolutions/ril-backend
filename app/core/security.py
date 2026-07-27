import os
from datetime import datetime, timedelta, timezone

import bcrypt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models import Traveller

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "dev-insecure-change-me")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 24 hours

# bcrypt rejects passwords longer than 72 bytes; truncate to stay within the limit.
_BCRYPT_MAX_BYTES = 72


def hash_password(password: str) -> str:
    pw = password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    return bcrypt.hashpw(pw, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str | None) -> bool:
    # Google-only accounts have no password hash; password login must fail for them.
    if not hashed:
        return False
    try:
        return bcrypt.checkpw(
            password.encode("utf-8")[:_BCRYPT_MAX_BYTES],
            hashed.encode("utf-8"),
        )
    except (ValueError, TypeError):
        return False


def create_access_token(traveller_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {"sub": str(traveller_id), "exp": expire}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


RESET_EXPIRE_MINUTES = int(os.getenv("RESET_EXPIRE_MINUTES", "30"))


def create_reset_token(traveller_id: int) -> str:
    """A short-lived token, marked purpose=reset, used only for password resets."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=RESET_EXPIRE_MINUTES)
    payload = {"sub": str(traveller_id), "purpose": "reset", "exp": expire}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_reset_token(token: str) -> int | None:
    """Return the traveller id if the token is a valid, unexpired reset token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("purpose") != "reset":
            return None
        return int(payload["sub"])
    except (JWTError, ValueError, KeyError):
        return None


# tokenUrl is only used for the OpenAPI docs "Authorize" button; the login
# endpoint itself accepts JSON. auto_error=False lets us raise a consistent 401.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login", auto_error=False)


def get_current_traveller(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Traveller:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        subject = payload.get("sub")
        if subject is None:
            raise credentials_exception
        traveller_id = int(subject)
    except (JWTError, ValueError):
        raise credentials_exception

    traveller = db.query(Traveller).filter(Traveller.id == traveller_id).first()
    if traveller is None:
        raise credentials_exception

    return traveller
