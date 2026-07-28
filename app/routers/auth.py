from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import os

from app.core.google_auth import GoogleAuthError, verify_google_id_token
from app.core.security import (
    create_access_token,
    create_reset_token,
    get_current_traveller,
    hash_password,
    verify_password,
    verify_reset_token,
)
from app.database.database import get_db
from app.models import Traveller
from app.schemas.auth_schema import (
    ForgotPasswordRequest,
    GoogleAuthRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    TravellerOut,
    TravellerUpdate,
)
from app.services.password_reset_service import (
    PasswordResetNotConfiguredError,
    PasswordResetSendError,
    send_password_reset_email,
)

router = APIRouter()

FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173").rstrip("/")


def _token_response(traveller: Traveller) -> TokenResponse:
    token = create_access_token(traveller.id)
    return TokenResponse(access_token=token, traveller=TravellerOut.model_validate(traveller))


def _parse_optional_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    email = payload.email.lower()

    existing = db.query(Traveller).filter(Traveller.email == email).first()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    traveller = Traveller(
        email=email,
        hashed_password=hash_password(payload.password),
        auth_provider="email",
        full_name=payload.full_name,
    )
    db.add(traveller)
    db.commit()
    db.refresh(traveller)

    return _token_response(traveller)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    traveller = (
        db.query(Traveller)
        .filter(Traveller.email == payload.email.lower())
        .first()
    )

    if traveller is None or not verify_password(payload.password, traveller.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    return _token_response(traveller)


@router.post("/google", response_model=TokenResponse)
def google_auth(payload: GoogleAuthRequest, db: Session = Depends(get_db)):
    try:
        identity = verify_google_id_token(payload.credential)
    except GoogleAuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))

    # Match an existing account by email (links a Google login to a prior signup),
    # otherwise create a new Google-backed account.
    traveller = db.query(Traveller).filter(Traveller.email == identity.email).first()

    if traveller is None:
        traveller = Traveller(
            email=identity.email,
            hashed_password=None,
            auth_provider="google",
            google_sub=identity.sub,
            full_name=identity.name,
        )
        db.add(traveller)
        db.commit()
        db.refresh(traveller)
    elif not traveller.google_sub:
        # Existing email account signing in with Google for the first time — link it.
        traveller.google_sub = identity.sub
        db.commit()
        db.refresh(traveller)

    return _token_response(traveller)


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    email = payload.email.lower()
    traveller = db.query(Traveller).filter(Traveller.email == email).first()

    # Only email accounts have a password to reset; Google accounts sign in with Google.
    if traveller is not None and traveller.auth_provider == "email":
        token = create_reset_token(traveller.id)
        reset_url = f"{FRONTEND_BASE_URL}/reset-password?token={token}"
        try:
            send_password_reset_email(traveller.email, reset_url)
        except (PasswordResetNotConfiguredError, PasswordResetSendError):
            # Don't leak configuration/delivery problems to the caller.
            pass

    # Always the same response, so the endpoint can't be used to probe which
    # emails have accounts.
    return {"ok": True, "message": "If an account exists for that email, a reset link has been sent."}


@router.post("/reset-password", response_model=TokenResponse)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    traveller_id = verify_reset_token(payload.token)
    if traveller_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This reset link is invalid or has expired.",
        )

    traveller = db.query(Traveller).filter(Traveller.id == traveller_id).first()
    if traveller is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This reset link is invalid or has expired.",
        )

    traveller.hashed_password = hash_password(payload.password)
    traveller.auth_provider = "email"
    db.commit()
    db.refresh(traveller)

    # Log them straight in after a successful reset.
    return _token_response(traveller)


@router.get("/me", response_model=TravellerOut)
def read_me(current: Traveller = Depends(get_current_traveller)):
    return current


@router.put("/me", response_model=TravellerOut)
def update_me(
    payload: TravellerUpdate,
    current: Traveller = Depends(get_current_traveller),
    db: Session = Depends(get_db),
):
    current.full_name = payload.full_name
    current.email = payload.email.lower()
    current.phone = payload.phone
    current.passport_number = payload.passport_number
    current.passport_expiry = _parse_optional_date(payload.passport_expiry)
    current.nationality = payload.nationality
    current.dietary_preferences = payload.dietary_preferences
    current.travel_style = payload.travel_style
    current.emergency_contact_name = payload.emergency_contact_name
    current.emergency_contact_phone = payload.emergency_contact_phone

    db.commit()
    db.refresh(current)
    return current
