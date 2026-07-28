import csv
import io

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.admin_security import create_admin_token, get_current_admin
from app.core.security import verify_password
from app.database.database import get_db
from app.models import Admin, Itinerary, Package, Place, Theme, Traveller
from app.schemas.admin_schema import (
    AdminLoginRequest,
    AdminOut,
    AdminTokenResponse,
    PackageIn,
    PackageOut,
    PlaceIn,
    PlaceOut,
    ThemeIn,
    ThemeOut,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


@router.post("/login", response_model=AdminTokenResponse)
def admin_login(payload: AdminLoginRequest, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.email == payload.email.lower()).first()
    if admin is None or not verify_password(payload.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )
    token = create_admin_token(admin.id)
    return AdminTokenResponse(access_token=token, admin=AdminOut.model_validate(admin))


@router.get("/me", response_model=AdminOut)
def admin_me(current: Admin = Depends(get_current_admin)):
    return current


# ---------------------------------------------------------------------------
# Themes
# ---------------------------------------------------------------------------


@router.get("/themes", response_model=list[ThemeOut])
def admin_list_themes(_: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    return db.query(Theme).order_by(Theme.sort_order, Theme.id).all()


@router.post("/themes", response_model=ThemeOut, status_code=status.HTTP_201_CREATED)
def admin_create_theme(
    payload: ThemeIn, _: Admin = Depends(get_current_admin), db: Session = Depends(get_db)
):
    theme = Theme(**payload.model_dump())
    db.add(theme)
    db.commit()
    db.refresh(theme)
    return theme


@router.put("/themes/{theme_id}", response_model=ThemeOut)
def admin_update_theme(
    theme_id: int,
    payload: ThemeIn,
    _: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    theme = db.query(Theme).filter(Theme.id == theme_id).first()
    if theme is None:
        raise HTTPException(status_code=404, detail="Theme not found.")
    for key, value in payload.model_dump().items():
        setattr(theme, key, value)
    db.commit()
    db.refresh(theme)
    return theme


@router.delete("/themes/{theme_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_theme(
    theme_id: int, _: Admin = Depends(get_current_admin), db: Session = Depends(get_db)
):
    theme = db.query(Theme).filter(Theme.id == theme_id).first()
    if theme is None:
        raise HTTPException(status_code=404, detail="Theme not found.")
    db.delete(theme)
    db.commit()


# ---------------------------------------------------------------------------
# Places
# ---------------------------------------------------------------------------


@router.get("/places", response_model=list[PlaceOut])
def admin_list_places(
    theme_id: int | None = None,
    _: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    query = db.query(Place)
    if theme_id is not None:
        query = query.filter(Place.theme_id == theme_id)
    return query.order_by(Place.sort_order, Place.id).all()


@router.post("/places", response_model=PlaceOut, status_code=status.HTTP_201_CREATED)
def admin_create_place(
    payload: PlaceIn, _: Admin = Depends(get_current_admin), db: Session = Depends(get_db)
):
    if db.query(Theme).filter(Theme.id == payload.theme_id).first() is None:
        raise HTTPException(status_code=400, detail="That theme does not exist.")
    place = Place(**payload.model_dump())
    db.add(place)
    db.commit()
    db.refresh(place)
    return place


@router.put("/places/{place_id}", response_model=PlaceOut)
def admin_update_place(
    place_id: int,
    payload: PlaceIn,
    _: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    place = db.query(Place).filter(Place.id == place_id).first()
    if place is None:
        raise HTTPException(status_code=404, detail="Place not found.")
    for key, value in payload.model_dump().items():
        setattr(place, key, value)
    db.commit()
    db.refresh(place)
    return place


@router.delete("/places/{place_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_place(
    place_id: int, _: Admin = Depends(get_current_admin), db: Session = Depends(get_db)
):
    place = db.query(Place).filter(Place.id == place_id).first()
    if place is None:
        raise HTTPException(status_code=404, detail="Place not found.")
    db.delete(place)
    db.commit()


# ---------------------------------------------------------------------------
# Packages
# ---------------------------------------------------------------------------


@router.get("/packages", response_model=list[PackageOut])
def admin_list_packages(_: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    return db.query(Package).order_by(Package.sort_order, Package.id).all()


@router.post("/packages", response_model=PackageOut, status_code=status.HTTP_201_CREATED)
def admin_create_package(
    payload: PackageIn, _: Admin = Depends(get_current_admin), db: Session = Depends(get_db)
):
    package = Package(**payload.model_dump())
    db.add(package)
    db.commit()
    db.refresh(package)
    return package


@router.put("/packages/{package_id}", response_model=PackageOut)
def admin_update_package(
    package_id: int,
    payload: PackageIn,
    _: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    package = db.query(Package).filter(Package.id == package_id).first()
    if package is None:
        raise HTTPException(status_code=404, detail="Package not found.")
    for key, value in payload.model_dump().items():
        setattr(package, key, value)
    db.commit()
    db.refresh(package)
    return package


@router.delete("/packages/{package_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_package(
    package_id: int, _: Admin = Depends(get_current_admin), db: Session = Depends(get_db)
):
    package = db.query(Package).filter(Package.id == package_id).first()
    if package is None:
        raise HTTPException(status_code=404, detail="Package not found.")
    db.delete(package)
    db.commit()


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------


@router.get("/reports/overview")
def admin_reports_overview(
    _: Admin = Depends(get_current_admin), db: Session = Depends(get_db)
):
    traveller_count = db.query(func.count(Traveller.id)).scalar() or 0
    google_count = (
        db.query(func.count(Traveller.id)).filter(Traveller.auth_provider == "google").scalar() or 0
    )

    recent = (
        db.query(Traveller).order_by(Traveller.created_at.desc()).limit(5).all()
    )
    recent_travellers = [
        {
            "fullName": t.full_name,
            "email": t.email,
            "provider": t.auth_provider,
            "createdAt": t.created_at.isoformat() if t.created_at else None,
        }
        for t in recent
    ]

    per_traveller_rows = (
        db.query(Traveller.full_name, Traveller.email, func.count(Itinerary.id))
        .outerjoin(Itinerary, Itinerary.traveller_id == Traveller.id)
        .group_by(Traveller.id)
        .order_by(func.count(Itinerary.id).desc())
        .limit(10)
        .all()
    )
    itineraries_per_traveller = [
        {"fullName": name, "email": email, "itineraries": count}
        for name, email, count in per_traveller_rows
    ]

    per_theme_rows = (
        db.query(Theme.title, func.count(Place.id))
        .outerjoin(Place, Place.theme_id == Theme.id)
        .group_by(Theme.id)
        .order_by(Theme.sort_order, Theme.id)
        .all()
    )
    places_per_theme = [{"theme": title, "places": count} for title, count in per_theme_rows]

    return {
        "travellers": traveller_count,
        "itineraries": db.query(func.count(Itinerary.id)).scalar() or 0,
        "themes": db.query(func.count(Theme.id)).scalar() or 0,
        "places": db.query(func.count(Place.id)).scalar() or 0,
        "packages": db.query(func.count(Package.id)).scalar() or 0,
        "googleTravellers": google_count,
        "emailTravellers": traveller_count - google_count,
        "recentTravellers": recent_travellers,
        "itinerariesPerTraveller": itineraries_per_traveller,
        "placesPerTheme": places_per_theme,
    }


@router.get("/reports/travellers.csv")
def admin_reports_travellers_csv(
    _: Admin = Depends(get_current_admin), db: Session = Depends(get_db)
):
    rows = (
        db.query(Traveller.full_name, Traveller.email, Traveller.auth_provider, Traveller.created_at, func.count(Itinerary.id))
        .outerjoin(Itinerary, Itinerary.traveller_id == Traveller.id)
        .group_by(Traveller.id)
        .order_by(Traveller.created_at.desc())
        .all()
    )

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Full Name", "Email", "Sign-in Method", "Registered", "Itineraries"])
    for name, email, provider, created_at, itinerary_count in rows:
        writer.writerow([
            name,
            email,
            provider,
            created_at.isoformat() if created_at else "",
            itinerary_count,
        ])

    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=travellers-report.csv"},
    )
