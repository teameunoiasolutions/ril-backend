from datetime import datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.database import Base


class Traveller(Base):
    """A registered traveller who logs into the traveller dashboard."""

    __tablename__ = "travellers"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    # Null for accounts created via Google (they authenticate through Google, not a password).
    hashed_password = Column(String(255), nullable=True)
    # How the account signs in: "email" or "google".
    auth_provider = Column(String(20), nullable=False, default="email")
    # Google's stable user id (the ID token "sub" claim); null for email accounts.
    google_sub = Column(String(255), nullable=True, unique=True, index=True)

    full_name = Column(String(255), nullable=False, default="")
    phone = Column(String(64), nullable=False, default="")
    passport_number = Column(String(64), nullable=False, default="")
    passport_expiry = Column(Date, nullable=True)
    nationality = Column(String(128), nullable=False, default="")
    dietary_preferences = Column(Text, nullable=False, default="")
    travel_style = Column(Text, nullable=False, default="")
    emergency_contact_name = Column(String(255), nullable=False, default="")
    emergency_contact_phone = Column(String(64), nullable=False, default="")

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    itineraries = relationship(
        "Itinerary",
        back_populates="traveller",
        cascade="all, delete-orphan",
        order_by="Itinerary.start_date",
    )


class Itinerary(Base):
    """A single voyage belonging to a traveller."""

    __tablename__ = "itineraries"

    # String primary key so the dashboard can generate ids client-side (e.g. "itinerary-1").
    id = Column(String(64), primary_key=True, index=True)
    traveller_id = Column(
        Integer,
        ForeignKey("travellers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title = Column(String(255), nullable=False, default="")
    destination = Column(String(255), nullable=False, default="")
    start_date = Column(String(32), nullable=False, default="")  # ISO date string (YYYY-MM-DD)
    end_date = Column(String(32), nullable=False, default="")
    cover_image = Column(Text, nullable=True)

    traveller = relationship("Traveller", back_populates="itineraries")
    stops = relationship(
        "ItineraryStop",
        back_populates="itinerary",
        cascade="all, delete-orphan",
        order_by="ItineraryStop.sort_order",
    )


class ItineraryStop(Base):
    """A single stop / activity within an itinerary."""

    __tablename__ = "itinerary_stops"

    id = Column(String(64), primary_key=True, index=True)
    itinerary_id = Column(
        String(64),
        ForeignKey("itineraries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    sort_order = Column(Integer, nullable=False, default=0)
    time = Column(String(32), nullable=False, default="")
    activity = Column(Text, nullable=False, default="")
    location = Column(Text, nullable=False, default="")
    notes = Column(Text, nullable=True)

    itinerary = relationship("Itinerary", back_populates="stops")
