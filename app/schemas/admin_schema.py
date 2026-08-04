from pydantic import BaseModel, ConfigDict, EmailStr, Field

# ---------------------------------------------------------------------------
# Admin auth
# ---------------------------------------------------------------------------


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str


class AdminOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    email: EmailStr
    full_name: str = Field(serialization_alias="fullName")


class AdminTokenResponse(BaseModel):
    access_token: str = Field(serialization_alias="accessToken")
    token_type: str = Field(default="bearer", serialization_alias="tokenType")
    admin: AdminOut


# ---------------------------------------------------------------------------
# Themes
# ---------------------------------------------------------------------------


class PlaceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    theme_id: int = Field(serialization_alias="themeId")
    name: str
    region: str
    description: str
    longitude: float | None = None
    latitude: float | None = None
    best_time: str = Field(serialization_alias="bestTime")
    activities: list[str] = []
    sort_order: int = Field(serialization_alias="sortOrder")


class ThemePackageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    theme_id: int = Field(serialization_alias="themeId")
    tier: str
    name: str
    days: int
    coverage: str
    summary: str
    hotel: str
    activities: list[str] = []
    inclusions: list[str] = []
    price_add: int = Field(serialization_alias="priceAdd")
    sort_order: int = Field(serialization_alias="sortOrder")


class ThemePackageIn(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    theme_id: int = Field(alias="themeId")
    tier: str = "glimpse"
    name: str
    days: int = 2
    coverage: str = "half"
    summary: str = ""
    hotel: str = ""
    activities: list[str] = []
    inclusions: list[str] = []
    price_add: int = Field(default=0, alias="priceAdd")
    sort_order: int = Field(default=0, alias="sortOrder")


class ThemeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    title: str
    description: str
    traveller: str
    encounter: str
    image_url: str | None = Field(default=None, serialization_alias="imageUrl")
    sort_order: int = Field(serialization_alias="sortOrder")
    places: list[PlaceOut] = []
    theme_packages: list[ThemePackageOut] = Field(
        default=[], serialization_alias="themePackages"
    )


class ThemeIn(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str
    description: str = ""
    traveller: str = ""
    encounter: str = ""
    image_url: str | None = Field(default=None, alias="imageUrl")
    sort_order: int = Field(default=0, alias="sortOrder")


class PlaceIn(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    theme_id: int = Field(alias="themeId")
    name: str
    region: str = ""
    description: str = ""
    longitude: float | None = None
    latitude: float | None = None
    best_time: str = Field(default="", alias="bestTime")
    activities: list[str] = []
    sort_order: int = Field(default=0, alias="sortOrder")


# ---------------------------------------------------------------------------
# Packages
# ---------------------------------------------------------------------------


class PackageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    numeral: str
    duration: str
    character: str
    route: list[str] = []
    inclusions: list[str] = []
    pace: str
    best_for: str = Field(serialization_alias="bestFor")
    reach: str
    image_url: str | None = Field(default=None, serialization_alias="imageUrl")
    price_from: int | None = Field(default=None, serialization_alias="priceFrom")
    sort_order: int = Field(serialization_alias="sortOrder")


class PackageIn(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    numeral: str = ""
    duration: str = ""
    character: str = ""
    route: list[str] = []
    inclusions: list[str] = []
    pace: str = ""
    best_for: str = Field(default="", alias="bestFor")
    reach: str = ""
    image_url: str | None = Field(default=None, alias="imageUrl")
    price_from: int | None = Field(default=None, alias="priceFrom")
    sort_order: int = Field(default=0, alias="sortOrder")


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------


class ReportsOverview(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    travellers: int
    itineraries: int
    themes: int
    places: int
    packages: int
    google_travellers: int = Field(serialization_alias="googleTravellers")
    email_travellers: int = Field(serialization_alias="emailTravellers")
    recent_travellers: list[dict] = Field(default=[], serialization_alias="recentTravellers")
    itineraries_per_traveller: list[dict] = Field(
        default=[], serialization_alias="itinerariesPerTraveller"
    )
    places_per_theme: list[dict] = Field(default=[], serialization_alias="placesPerTheme")
