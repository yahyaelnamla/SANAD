"""Pydantic schemas for authentication endpoints."""

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """User registration payload."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    locale: str = Field(default="ar", pattern=r"^(ar|en)$")


class LoginRequest(BaseModel):
    """User login payload."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(BaseModel):
    """JWT access token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserProfileResponse(BaseModel):
    """Authenticated user profile."""

    id: str
    email: str
    role: str
    locale: str
    subscription_tier: str = "free"
    subscription_status: str = "active"
    onboarding_completed: bool = False
    auth_provider: str = "email"
