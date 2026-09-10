from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

EnquiryKind = Literal["planned", "unplanned"]
EnquirySource = Literal["contact", "itinerary", "theme"]
EnquiryStatus = Literal["new", "read", "closed"]


class EnquiryIn(BaseModel):
    """What the public site posts when a visitor sends an enquiry."""

    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    phone: str = Field(default="", max_length=64)
    message: str = Field(default="", max_length=5000)

    source: EnquirySource = "contact"
    # The journey or theme being asked about. Its presence is what makes an
    # enquiry "planned", so the server derives `kind` from it rather than
    # trusting the client to classify itself.
    topic: str | None = Field(default=None, max_length=500)
    page_url: str = Field(default="", max_length=2000, alias="pageUrl")

    @field_validator("name", "phone", "message", "page_url")
    @classmethod
    def _strip(cls, value: str) -> str:
        return value.strip()

    @field_validator("topic")
    @classmethod
    def _strip_topic(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    @property
    def kind(self) -> EnquiryKind:
        return "planned" if self.topic else "unplanned"


class EnquiryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    kind: str
    source: str
    topic: str | None = None
    name: str
    email: EmailStr
    phone: str
    message: str
    page_url: str = Field(serialization_alias="pageUrl")
    status: str
    created_at: datetime = Field(serialization_alias="createdAt")


class EnquiryStatusIn(BaseModel):
    status: EnquiryStatus
