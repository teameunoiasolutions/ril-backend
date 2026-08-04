"""Public, unauthenticated read endpoints so the live site reads content from the DB."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models import Package, Place, Theme, ThemePackage
from app.schemas.admin_schema import PackageOut, PlaceOut, ThemeOut, ThemePackageOut

router = APIRouter()


@router.get("/themes", response_model=list[ThemeOut])
def list_themes(db: Session = Depends(get_db)):
    return db.query(Theme).order_by(Theme.sort_order, Theme.id).all()


@router.get("/places", response_model=list[PlaceOut])
def list_places(theme_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Place)
    if theme_id is not None:
        query = query.filter(Place.theme_id == theme_id)
    return query.order_by(Place.sort_order, Place.id).all()


@router.get("/theme-packages", response_model=list[ThemePackageOut])
def list_theme_packages(theme_id: int | None = None, db: Session = Depends(get_db)):
    """The Glimpse / The Immersion sub-packages sold under each theme."""
    query = db.query(ThemePackage)
    if theme_id is not None:
        query = query.filter(ThemePackage.theme_id == theme_id)
    return query.order_by(ThemePackage.sort_order, ThemePackage.id).all()


@router.get("/packages", response_model=list[PackageOut])
def list_packages(db: Session = Depends(get_db)):
    return db.query(Package).order_by(Package.sort_order, Package.id).all()
