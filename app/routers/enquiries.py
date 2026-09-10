from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.admin_security import get_current_admin
from app.database.database import get_db
from app.models import Admin, Enquiry
from app.schemas.enquiry_schema import EnquiryIn, EnquiryOut, EnquiryStatusIn

# Public: the website posts here. No auth — anyone may send an enquiry.
router = APIRouter()

# Admin: the desk reads and triages them. Mounted under /api/admin.
admin_router = APIRouter()


@router.post("", response_model=EnquiryOut, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=EnquiryOut, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def create_enquiry(payload: EnquiryIn, db: Session = Depends(get_db)):
    """Record an enquiry sent from any of the public enquiry forms."""
    enquiry = Enquiry(
        kind=payload.kind,
        source=payload.source,
        topic=payload.topic,
        name=payload.name,
        email=payload.email.lower(),
        phone=payload.phone,
        message=payload.message,
        page_url=payload.page_url,
    )
    db.add(enquiry)
    db.commit()
    db.refresh(enquiry)
    return enquiry


@admin_router.get("/enquiries", response_model=list[EnquiryOut])
def admin_list_enquiries(
    kind: str | None = Query(default=None, pattern="^(planned|unplanned)$"),
    enquiry_status: str | None = Query(default=None, alias="status", pattern="^(new|read|closed)$"),
    limit: int = Query(default=200, ge=1, le=1000),
    _: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    query = db.query(Enquiry)
    if kind:
        query = query.filter(Enquiry.kind == kind)
    if enquiry_status:
        query = query.filter(Enquiry.status == enquiry_status)
    return query.order_by(Enquiry.created_at.desc()).limit(limit).all()


@admin_router.patch("/enquiries/{enquiry_id}", response_model=EnquiryOut)
def admin_update_enquiry_status(
    enquiry_id: int,
    payload: EnquiryStatusIn,
    _: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    enquiry = db.query(Enquiry).filter(Enquiry.id == enquiry_id).first()
    if enquiry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enquiry not found.")
    enquiry.status = payload.status
    db.commit()
    db.refresh(enquiry)
    return enquiry
