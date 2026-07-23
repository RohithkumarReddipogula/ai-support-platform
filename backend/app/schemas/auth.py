import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional


# --- Tenant schemas ---

class TenantCreate(BaseModel):
    name: str
    slug: str


class TenantOut(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    api_key: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# --- User schemas ---

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    tenant_name: str  # Creates a new tenant on registration


class UserOut(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    tenant: Optional[TenantOut] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# --- Token schemas ---

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class MessageResponse(BaseModel):
    message: str
