from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.database.database import Base


class Enquiry(Base):
    """An enquiry raised from the public site.

    Every enquiry form on the website lands here, whether the visitor was
    reading a specific journey or simply reached the contact page. `kind`
    separates the two so the desk can triage:

    * "planned"   — the enquiry names something concrete (a journey, a theme),
                    so `topic` carries what was on screen when they asked.
    * "unplanned" — a general enquiry with nothing attached yet.
    """

    __tablename__ = "enquiries"

    id = Column(Integer, primary_key=True, index=True)

    kind = Column(String(20), nullable=False, default="unplanned", index=True)
    # Which form it came from: "contact", "itinerary" or "theme".
    source = Column(String(40), nullable=False, default="contact", index=True)
    # The journey or theme the enquiry was about; null for a general enquiry.
    topic = Column(Text, nullable=True)

    name = Column(String(255), nullable=False, default="")
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(64), nullable=False, default="")
    message = Column(Text, nullable=False, default="")

    # The page the enquiry was sent from, for context when following up.
    page_url = Column(Text, nullable=False, default="")

    # Desk triage: "new", "read" or "closed".
    status = Column(String(20), nullable=False, default="new", index=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
