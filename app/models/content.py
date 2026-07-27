from sqlalchemy import Column, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from app.database.database import Base


class Theme(Base):
    """An Expectations theme shown on the public site (and its map shortcuts)."""

    __tablename__ = "themes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False, default="")
    traveller = Column(String(255), nullable=False, default="")
    encounter = Column(String(255), nullable=False, default="")
    image_url = Column(Text, nullable=True)
    sort_order = Column(Integer, nullable=False, default=0)

    places = relationship(
        "Place",
        back_populates="theme",
        cascade="all, delete-orphan",
        order_by="Place.sort_order",
    )


class Place(Base):
    """A place shown under a theme (name, region, coordinates, things to do)."""

    __tablename__ = "places"

    id = Column(Integer, primary_key=True, index=True)
    theme_id = Column(
        Integer, ForeignKey("themes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name = Column(String(255), nullable=False)
    region = Column(String(255), nullable=False, default="")
    description = Column(Text, nullable=False, default="")
    longitude = Column(Float, nullable=True)
    latitude = Column(Float, nullable=True)
    best_time = Column(String(128), nullable=False, default="")
    activities = Column(JSON, nullable=False, default=list)  # list[str]
    sort_order = Column(Integer, nullable=False, default=0)

    theme = relationship("Theme", back_populates="places")


class Package(Base):
    """A public template itinerary (Discovery / Deep Dive / Dynasty style)."""

    __tablename__ = "packages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    numeral = Column(String(8), nullable=False, default="")
    duration = Column(String(64), nullable=False, default="")
    character = Column(Text, nullable=False, default="")
    route = Column(JSON, nullable=False, default=list)  # list[str]
    inclusions = Column(JSON, nullable=False, default=list)  # list[str]
    pace = Column(String(64), nullable=False, default="")
    best_for = Column(String(255), nullable=False, default="")
    reach = Column(String(255), nullable=False, default="")
    image_url = Column(Text, nullable=True)
    price_from = Column(Integer, nullable=True)  # USD per person; null = hidden
    sort_order = Column(Integer, nullable=False, default=0)
