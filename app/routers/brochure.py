from fastapi import APIRouter, HTTPException

from app.schemas.brochure_schema import BrochureRequest
from app.services.brochure_service import (
    BrochureNotConfiguredError,
    BrochureSendError,
    send_brochure_email,
)

router = APIRouter()


@router.post("/request")
def request_brochure(payload: BrochureRequest):
    try:
        send_brochure_email(payload.email)
    except BrochureNotConfiguredError:
        raise HTTPException(
            status_code=500,
            detail="Brochure delivery is not configured yet. Please try again later.",
        )
    except BrochureSendError:
        raise HTTPException(
            status_code=502,
            detail="We could not send the brochure right now. Please try again shortly.",
        )

    return {"ok": True}
