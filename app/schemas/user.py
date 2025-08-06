from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserRegistration(BaseModel):
    email: EmailStr
    password: str


class ActivationToken(BaseModel):
    token: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
