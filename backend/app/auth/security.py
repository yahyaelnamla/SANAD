"""Password hashing and JWT token utilities."""

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID


def _patch_bcrypt_for_passlib() -> None:
    """passlib 1.7.4 expects bcrypt.__about__.__version__ (removed in bcrypt 4.1+)."""
    try:
        import bcrypt

        if not hasattr(bcrypt, "__about__"):
            bcrypt.__about__ = type(  # type: ignore[attr-defined]
                "about",
                (object,),
                {"__version__": getattr(bcrypt, "__version__", "4.0.1")},
            )
    except Exception:
        pass


_patch_bcrypt_for_passlib()

from jose import JWTError, jwt
from passlib.context import CryptContext

from backend.app.config.settings import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plaintext password with bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    *,
    user_id: UUID,
    email: str,
    role: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT access token."""
    settings = get_settings()
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.jwt_expire_minutes)
    )
    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT access token."""
    settings = get_settings()
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise ValueError("Invalid or expired token") from exc
