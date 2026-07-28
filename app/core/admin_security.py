from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.security import JWT_ALGORITHM, JWT_SECRET
from app.database.database import get_db
from app.models import Admin

ADMIN_TOKEN_EXPIRE_MINUTES = 720  # 12 hours


def create_admin_token(admin_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ADMIN_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(admin_id), "scope": "admin", "exp": expire}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


admin_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/admin/login", auto_error=False)


def get_current_admin(
    token: str | None = Depends(admin_oauth2_scheme),
    db: Session = Depends(get_db),
) -> Admin:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Administrator authentication required.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("scope") != "admin":
            raise credentials_exception
        admin_id = int(payload["sub"])
    except (JWTError, ValueError, KeyError):
        raise credentials_exception

    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if admin is None:
        raise credentials_exception

    return admin
