"""Verify Google Sign-In ID tokens.

The dashboard uses Google Identity Services: after the user signs in with Google
the frontend receives an ID token (a JWT) and posts it here. We verify that token
directly with Google and return the identity claims we need.

Set GOOGLE_CLIENT_ID in the backend .env to the OAuth 2.0 Web client ID created in
the Google Cloud console. Verification is skipped-as-invalid if it is not set.
"""
import os

import httpx
from dotenv import load_dotenv

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"


class GoogleAuthError(Exception):
    """Raised when a Google ID token cannot be verified."""


class GoogleIdentity:
    def __init__(self, email: str, sub: str, name: str, email_verified: bool):
        self.email = email
        self.sub = sub
        self.name = name
        self.email_verified = email_verified


def verify_google_id_token(credential: str) -> GoogleIdentity:
    if not GOOGLE_CLIENT_ID:
        raise GoogleAuthError("Google sign-in is not configured on the server.")

    try:
        response = httpx.get(
            _TOKENINFO_URL, params={"id_token": credential}, timeout=10.0
        )
    except httpx.HTTPError as exc:  # network failure
        raise GoogleAuthError("Could not reach Google to verify sign-in.") from exc

    if response.status_code != 200:
        raise GoogleAuthError("Invalid Google sign-in token.")

    data = response.json()

    # The token must have been issued for *our* client id.
    if data.get("aud") != GOOGLE_CLIENT_ID:
        raise GoogleAuthError("Google token was issued for a different application.")

    email = data.get("email")
    sub = data.get("sub")
    if not email or not sub:
        raise GoogleAuthError("Google token did not include an email.")

    # Google returns these booleans as the strings "true"/"false".
    email_verified = str(data.get("email_verified", "false")).lower() == "true"
    if not email_verified:
        raise GoogleAuthError("This Google account's email is not verified.")

    return GoogleIdentity(
        email=email.lower(),
        sub=sub,
        name=data.get("name", ""),
        email_verified=email_verified,
    )
