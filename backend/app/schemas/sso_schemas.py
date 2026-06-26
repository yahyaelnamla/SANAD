"""Single sign-on schemas."""

from pydantic import BaseModel, EmailStr, Field


class SsoProviderSchema(BaseModel):
    """Enabled SSO identity provider."""

    id: str
    name: str
    enabled: bool
    demo_mode: bool = False


class SsoStartRequest(BaseModel):
    """Begin an SSO authorization flow."""

    provider: str = Field(pattern=r"^(google|microsoft)$")
    redirect_uri: str | None = None


class SsoStartResponse(BaseModel):
    """SSO flow start payload."""

    provider: str
    mode: str
    session_id: str | None = None
    authorization_url: str | None = None


class SsoCompleteRequest(BaseModel):
    """Complete SSO login (OAuth code or demo session)."""

    provider: str = Field(pattern=r"^(google|microsoft)$")
    session_id: str | None = None
    code: str | None = None
    redirect_uri: str | None = None
    email: EmailStr | None = None
    display_name: str | None = Field(default=None, max_length=120)


class SsoCompleteResponse(BaseModel):
    """JWT response after successful SSO."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    is_new_user: bool
