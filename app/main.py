from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import Base, engine
from app.routers import admin, assistant, auth, brochure, content, itineraries

# Import models so their tables are registered on Base before create_all().
from app import models  # noqa: F401

app = FastAPI()

# Create any missing tables on startup. (For real schema migrations, use Alembic.)
Base.metadata.create_all(bind=engine)

# Allow frontend to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development/testing only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "message": "Tourist API Running"
    }

app.include_router(
    assistant.router,
    prefix="/api/assistant",
    tags=["AI Assistant"]
)

app.include_router(
    brochure.router,
    prefix="/api/brochure",
    tags=["Brochure"]
)

app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["Auth"]
)

app.include_router(
    itineraries.router,
    prefix="/api/traveller",
    tags=["Traveller"]
)

app.include_router(
    content.router,
    prefix="/api/content",
    tags=["Public Content"]
)

app.include_router(
    admin.router,
    prefix="/api/admin",
    tags=["Admin"]
)
