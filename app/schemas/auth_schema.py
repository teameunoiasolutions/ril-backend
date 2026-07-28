from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# ---------------------------------------------------------------------------
# Output schemas — field names are snake_case (read from ORM) but serialize to
# the camelCase keys the traveller dashboard's types.ts already expects.
# FastAPI serializes response models by alias, so no mapping is needed client-side.
# ---------------------------------------------------------------------------


class ItineraryStopOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    time: str
    activity: str
    location: str
    notes: str | None = None


class ItineraryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    title: str
    destination: str
    start_date: str = Field(serialization_alias="startDate")
    end_date: str = Field(serialization_alias="endDate")
    cover_image: str | None = Field(default=None, serialization_alias="coverImage")
    stops: list[ItineraryStopOut] = []


class TravellerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    full_name: str = Field(serialization_alias="fullName")
    email: EmailStr
    phone: str
    passport_number: str = Field(serialization_alias="passportNumber")
    passport_expiry: date | None = Field(default=None, serialization_alias="passportExpiry")
    nationality: str
    dietary_preferences: str = Field(serialization_alias="dietaryPreferences")
    travel_style: str = Field(serialization_alias="travelStyle")
    emergency_contact_name: str = Field(serialization_alias="emergencyContactName")
    emergency_contact_phone: str = Field(serialization_alias="emergencyContactPhone")


# ---------------------------------------------------------------------------
# Auth request / response schemas
# ---------------------------------------------------------------------------


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(default="", alias="fullName")


class GoogleAuthRequest(BaseModel):
    # The Google Identity Services ID token returned to the frontend.
    credential: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    password: str = Field(min_length=8)


class TokenResponse(BaseModel):
    access_token: str = Field(serialization_alias="accessToken")
    token_type: str = Field(default="bearer", serialization_alias="tokenType")
    traveller: TravellerOut


# ---------------------------------------------------------------------------
# Input schemas — accept the camelCase keys the dashboard sends.
# ---------------------------------------------------------------------------


class TravellerUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    full_name: str = Field(default="", alias="fullName")
    email: EmailStr
    phone: str = ""
    passport_number: str = Field(default="", alias="passportNumber")
    # Accept a raw string ("YYYY-MM-DD" or "") — the router converts it to a date.
    passport_expiry: str | None = Field(default=None, alias="passportExpiry")
    nationality: str = ""
    dietary_preferences: str = Field(default="", alias="dietaryPreferences")
    travel_style: str = Field(default="", alias="travelStyle")
    emergency_contact_name: str = Field(default="", alias="emergencyContactName")
    emergency_contact_phone: str = Field(default="", alias="emergencyContactPhone")


class ItineraryStopIn(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    time: str = ""
    activity: str = ""
    location: str = ""
    notes: str | None = None


class ItineraryIn(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    title: str = ""
    destination: str = ""
    start_date: str = Field(default="", alias="startDate")
    end_date: str = Field(default="", alias="endDate")
    cover_image: str | None = Field(default=None, alias="coverImage")
    stops: list[ItineraryStopIn] = []


class ItinerariesReplace(BaseModel):
    itineraries: list[ItineraryIn] = []
