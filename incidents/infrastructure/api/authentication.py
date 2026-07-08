"""Custom JWT authentication using PyJWT."""

from dataclasses import dataclass
from typing import Any

import jwt
from django.conf import settings
from rest_framework.authentication import (
    BaseAuthentication,
    get_authorization_header,
)
from rest_framework.exceptions import AuthenticationFailed


@dataclass
class AuthenticatedUser:
    """User information extracted from the JWT."""

    id: str
    role: str
    email: str

    @property
    def is_authenticated(self) -> bool:
        return True


class JWTAuthentication(BaseAuthentication):
    """Authenticate requests using RS256 JWT tokens."""

    def authenticate(
        self, request: Any
    ) -> tuple[AuthenticatedUser, dict[str, Any]] | None:
        auth = get_authorization_header(request).split()

        if not auth:
            return None

        if len(auth) != 2 or auth[0].lower() != b"bearer":
            raise AuthenticationFailed("Invalid Authorization header.")

        # Verificar que la llave pública fue cargada
        if not settings.JWT_PUBLIC_KEY.strip():
            raise AuthenticationFailed("JWT public key is not configured.")

        token = auth[1].decode("utf-8")

        try:
            payload: dict[str, Any] = jwt.decode(
                token,
                settings.JWT_PUBLIC_KEY.strip(),
                algorithms=[settings.JWT_ALGORITHM],
            )
        except jwt.ExpiredSignatureError as exc:
            raise AuthenticationFailed("Token has expired.") from exc
        except jwt.InvalidTokenError as exc:
            raise AuthenticationFailed("Invalid authentication token.") from exc

        user_id = payload.get("sub")
        role = payload.get("role")
        email = payload.get("email", "")

        if not user_id or not role:
            raise AuthenticationFailed("Token is missing required claims.")

        user = AuthenticatedUser(
            id=str(user_id),
            role=str(role),
            email=str(email),
        )

        return user, payload
