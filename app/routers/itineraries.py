from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_traveller
from app.database.database import get_db
from app.models import Itinerary, ItineraryStop, Traveller
from app.schemas.auth_schema import ItinerariesReplace, ItineraryOut

router = APIRouter()


@router.get("/itineraries", response_model=list[ItineraryOut])
def list_itineraries(current: Traveller = Depends(get_current_traveller)):
    # relationship is ordered by start_date; stops are ordered by sort_order.
    return current.itineraries


@router.put("/itineraries", response_model=list[ItineraryOut])
def replace_itineraries(
    payload: ItinerariesReplace,
    current: Traveller = Depends(get_current_traveller),
    db: Session = Depends(get_db),
):
    """Replace the traveller's full set of itineraries with the submitted list.

    The dashboard edits itineraries as one collection, so a full replace keeps
    the client and database in sync without diffing individual records.
    """
    # Delete via the ORM (not a bulk query.delete) so the delete-orphan cascade
    # removes each itinerary's stops too. A bulk delete would leave orphaned
    # stop rows, and re-inserting stops that keep their ids would then collide
    # on the primary key.
    existing = db.query(Itinerary).filter(Itinerary.traveller_id == current.id).all()
    for itinerary in existing:
        db.delete(itinerary)
    db.flush()

    for itinerary_in in payload.itineraries:
        itinerary = Itinerary(
            id=itinerary_in.id,
            traveller_id=current.id,
            title=itinerary_in.title,
            destination=itinerary_in.destination,
            start_date=itinerary_in.start_date,
            end_date=itinerary_in.end_date,
            cover_image=itinerary_in.cover_image,
        )
        for index, stop_in in enumerate(itinerary_in.stops):
            itinerary.stops.append(
                ItineraryStop(
                    id=stop_in.id,
                    sort_order=index,
                    time=stop_in.time,
                    activity=stop_in.activity,
                    location=stop_in.location,
                    notes=stop_in.notes,
                )
            )
        db.add(itinerary)

    db.commit()

    db.refresh(current)
    return current.itineraries
