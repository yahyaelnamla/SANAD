"""Single sign-on — Google/Microsoft OAuth with demo fallback."""

from __future__ import annotations

import secrets
from urllib.parse import urlencode

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.auth.security import create_access_token, hash_password
from backend.app.config.settings import get_settings
from backend.app.exceptions import UnauthorizedError, ValidationError
from backend.app.models.enums import AuthProvider, UserRole
from backend.app.models.user import User
from backend.app.repositories.user_repository import UserRepository
from backend.app.schemas.sso_schemas import (
    SsoCompleteRequest,
    SsoCompleteResponse,
    SsoProviderSchema,
    SsoStartRequest,
    SsoStartResponse,
)

_DEMO_SESSIONS: dict[str, dict[str, str]] = {}


class SsoService:
    """OAuth2 SSO with demo mode for hackathon environments."""

    PROVIDER_NAMES = {
        "google": "Google",
        "microsoft": "Microsoft",
    }

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)
        self.settings = get_settings()

    def list_providers(self) -> list[SsoProviderSchema]:
        providers: list[SsoProviderSchema] = []
        for provider_id in ("google", "microsoft"):
            enabled = self._provider_configured(provider_id) or self.settings.sso_demo_mode
            providers.append(
                SsoProviderSchema(
                    id=provider_id,
                    name=self.PROVIDER_NAMES[provider_id],
                    enabled=enabled,
                    demo_mode=(
                        self.settings.sso_demo_mode and not self._provider_configured(provider_id)
                    ),
                )
            )
        return providers

    async def start(self, request: SsoStartRequest) -> SsoStartResponse:
        provider = request.provider
        if not self._provider_enabled(provider):
            raise ValidationError(f"SSO provider '{provider}' is not enabled.")

        if self._provider_configured(provider):
            session_id = secrets.token_urlsafe(16)
            _DEMO_SESSIONS[session_id] = {"provider": provider}
            auth_url = self._build_authorization_url(provider, request.redirect_uri, session_id)
            return SsoStartResponse(
                provider=provider,
                mode="oauth",
                session_id=session_id,
                authorization_url=auth_url,
            )

        session_id = secrets.token_urlsafe(24)
        _DEMO_SESSIONS[session_id] = {"provider": provider, "mode": "demo"}
        return SsoStartResponse(provider=provider, mode="demo", session_id=session_id)

    async def complete(self, request: SsoCompleteRequest) -> SsoCompleteResponse:
        provider = request.provider
        if not self._provider_enabled(provider):
            raise ValidationError(f"SSO provider '{provider}' is not enabled.")

        if request.code and self._provider_configured(provider):
            email, subject = await self._exchange_oauth_code(
                provider,
                request.code,
                request.redirect_uri,
            )
        elif request.session_id and request.email:
            session = _DEMO_SESSIONS.pop(request.session_id, None)
            if session is None or session.get("provider") != provider:
                raise UnauthorizedError("Invalid or expired SSO session.")
            email = request.email.lower()
            subject = f"demo:{provider}:{email}"
        else:
            raise ValidationError("Provide OAuth code or demo session with email.")

        auth_provider = AuthProvider(provider)
        user, is_new = await self._find_or_create_sso_user(
            email=email,
            subject=subject,
            provider=auth_provider,
        )
        token = create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role.value,
        )
        return SsoCompleteResponse(
            access_token=token,
            expires_in=self.settings.jwt_expire_minutes * 60,
            is_new_user=is_new,
        )

    def _provider_enabled(self, provider: str) -> bool:
        return self._provider_configured(provider) or self.settings.sso_demo_mode

    def _provider_configured(self, provider: str) -> bool:
        if provider == "google":
            return bool(self.settings.google_client_id and self.settings.google_client_secret)
        if provider == "microsoft":
            return bool(
                self.settings.microsoft_client_id and self.settings.microsoft_client_secret
            )
        return False

    def _build_authorization_url(
        self,
        provider: str,
        redirect_uri: str | None,
        state: str,
    ) -> str:
        redirect = redirect_uri or self.settings.sso_redirect_uri
        if provider == "google":
            params = {
                "client_id": self.settings.google_client_id,
                "redirect_uri": redirect,
                "response_type": "code",
                "scope": "openid email profile",
                "state": state,
                "access_type": "online",
                "prompt": "select_account",
            }
            return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
        params = {
            "client_id": self.settings.microsoft_client_id,
            "redirect_uri": redirect,
            "response_type": "code",
            "scope": "openid email profile User.Read",
            "state": state,
            "response_mode": "query",
        }
        return (
            "https://login.microsoftonline.com/common/oauth2/v2.0/authorize?"
            f"{urlencode(params)}"
        )

    async def _exchange_oauth_code(
        self,
        provider: str,
        code: str,
        redirect_uri: str | None,
    ) -> tuple[str, str]:
        redirect = redirect_uri or self.settings.sso_redirect_uri
        if provider == "google":
            token_url = "https://oauth2.googleapis.com/token"
            data = {
                "code": code,
                "client_id": self.settings.google_client_id,
                "client_secret": self.settings.google_client_secret,
                "redirect_uri": redirect,
                "grant_type": "authorization_code",
            }
            profile_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        else:
            token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
            data = {
                "code": code,
                "client_id": self.settings.microsoft_client_id,
                "client_secret": self.settings.microsoft_client_secret,
                "redirect_uri": redirect,
                "grant_type": "authorization_code",
                "scope": "openid email profile User.Read",
            }
            profile_url = "https://graph.microsoft.com/v1.0/me"

        async with httpx.AsyncClient(timeout=20.0) as client:
            token_resp = await client.post(token_url, data=data)
            if token_resp.status_code >= 400:
                raise UnauthorizedError("OAuth token exchange failed.")
            access_token = token_resp.json().get("access_token")
            if not access_token:
                raise UnauthorizedError("OAuth token missing from provider response.")

            profile_resp = await client.get(
                profile_url,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if profile_resp.status_code >= 400:
                raise UnauthorizedError("Failed to fetch SSO profile.")

            profile = profile_resp.json()
            email = profile.get("email") or profile.get("mail") or profile.get("userPrincipalName")
            subject = profile.get("id") or profile.get("sub")
            if not email or not subject:
                raise UnauthorizedError("SSO profile missing required identity fields.")
            return email.lower(), str(subject)

    async def _find_or_create_sso_user(
        self,
        *,
        email: str,
        subject: str,
        provider: AuthProvider,
    ) -> tuple[User, bool]:
        existing = await self.user_repo.get_by_sso_subject(provider.value, subject)
        if existing is not None:
            return existing, False

        by_email = await self.user_repo.get_by_email(email)
        if by_email is not None:
            by_email.auth_provider = provider
            by_email.sso_subject = subject
            await self.user_repo.session.flush()
            await self.user_repo.session.refresh(by_email)
            return by_email, False

        user = User(
            email=email,
            password_hash=hash_password(secrets.token_urlsafe(32)),
            role=UserRole.USER,
            locale="en",
            auth_provider=provider,
            sso_subject=subject,
            onboarding_completed=False,
        )
        created = await self.user_repo.create(user)
        return created, True
