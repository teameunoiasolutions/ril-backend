from pydantic import BaseModel, EmailStr


class BrochureRequest(BaseModel):
    email: EmailStr
