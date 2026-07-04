from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    message: str
    isPersonalized: bool = False

    mood: Optional[str] = None
    identity: Optional[str] = None