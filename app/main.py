from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import assistant

app = FastAPI()

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