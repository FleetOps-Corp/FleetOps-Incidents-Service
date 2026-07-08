"""Unit tests for custom JWT authentication."""

from unittest.mock import Mock, patch

import jwt
import pytest
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed

from incidents.infrastructure.api.authentication import (
    AuthenticatedUser,
    JWTAuthentication,
)


class TestAuthenticatedUser:
    """Tests for AuthenticatedUser."""

    def test_is_authenticated_returns_true(self):
        user = AuthenticatedUser(
            id="123",
            role="ADMIN",
            email="admin@test.com",
        )
        assert user.is_authenticated is True


class TestJWTAuthentication:
    """Tests for JWTAuthentication."""

    def setup_method(self):
        self.authentication = JWTAuthentication()
        self.request = Mock()

    @patch("incidents.infrastructure.api.authentication.get_authorization_header")
    def test_returns_none_when_no_authorization_header(
        self,
        mock_header,
    ):
        mock_header.return_value = b""

        assert self.authentication.authenticate(self.request) is None

    @patch("incidents.infrastructure.api.authentication.get_authorization_header")
    def test_invalid_authorization_header(
        self,
        mock_header,
    ):
        mock_header.return_value = b"Bearer"

        with pytest.raises(AuthenticationFailed):
            self.authentication.authenticate(self.request)

    @patch("incidents.infrastructure.api.authentication.get_authorization_header")
    def test_public_key_not_configured(
        self,
        mock_header,
        monkeypatch,
    ):
        mock_header.return_value = b"Bearer token"

        monkeypatch.setattr(settings, "JWT_PUBLIC_KEY", "")

        with pytest.raises(AuthenticationFailed) as exc:
            self.authentication.authenticate(self.request)

        assert "JWT public key is not configured." in str(exc.value)

    @patch("incidents.infrastructure.api.authentication.jwt.decode")
    @patch("incidents.infrastructure.api.authentication.get_authorization_header")
    def test_expired_token(
        self,
        mock_header,
        mock_decode,
        monkeypatch,
    ):
        mock_header.return_value = b"Bearer token"

        monkeypatch.setattr(settings, "JWT_PUBLIC_KEY", "public-key")
        monkeypatch.setattr(settings, "JWT_ALGORITHM", "RS256")

        mock_decode.side_effect = jwt.ExpiredSignatureError()

        with pytest.raises(AuthenticationFailed) as exc:
            self.authentication.authenticate(self.request)

        assert "Token has expired." in str(exc.value)

    @patch("incidents.infrastructure.api.authentication.jwt.decode")
    @patch("incidents.infrastructure.api.authentication.get_authorization_header")
    def test_invalid_token(
        self,
        mock_header,
        mock_decode,
        monkeypatch,
    ):
        mock_header.return_value = b"Bearer token"

        monkeypatch.setattr(settings, "JWT_PUBLIC_KEY", "public-key")
        monkeypatch.setattr(settings, "JWT_ALGORITHM", "RS256")

        mock_decode.side_effect = jwt.InvalidTokenError()

        with pytest.raises(AuthenticationFailed) as exc:
            self.authentication.authenticate(self.request)

        assert "Invalid authentication token." in str(exc.value)

    @patch("incidents.infrastructure.api.authentication.jwt.decode")
    @patch("incidents.infrastructure.api.authentication.get_authorization_header")
    def test_missing_sub_claim(
        self,
        mock_header,
        mock_decode,
        monkeypatch,
    ):
        mock_header.return_value = b"Bearer token"

        monkeypatch.setattr(settings, "JWT_PUBLIC_KEY", "public-key")
        monkeypatch.setattr(settings, "JWT_ALGORITHM", "RS256")

        mock_decode.return_value = {
            "role": "ADMIN",
            "email": "admin@test.com",
        }

        with pytest.raises(AuthenticationFailed):
            self.authentication.authenticate(self.request)

    @patch("incidents.infrastructure.api.authentication.jwt.decode")
    @patch("incidents.infrastructure.api.authentication.get_authorization_header")
    def test_missing_role_claim(
        self,
        mock_header,
        mock_decode,
        monkeypatch,
    ):
        mock_header.return_value = b"Bearer token"

        monkeypatch.setattr(settings, "JWT_PUBLIC_KEY", "public-key")
        monkeypatch.setattr(settings, "JWT_ALGORITHM", "RS256")

        mock_decode.return_value = {
            "sub": "123",
            "email": "admin@test.com",
        }

        with pytest.raises(AuthenticationFailed):
            self.authentication.authenticate(self.request)

    @patch("incidents.infrastructure.api.authentication.jwt.decode")
    @patch("incidents.infrastructure.api.authentication.get_authorization_header")
    def test_successful_authentication(
        self,
        mock_header,
        mock_decode,
        monkeypatch,
    ):
        mock_header.return_value = b"Bearer valid-token"

        monkeypatch.setattr(settings, "JWT_PUBLIC_KEY", "public-key")
        monkeypatch.setattr(settings, "JWT_ALGORITHM", "RS256")

        payload = {
            "sub": "123",
            "role": "ADMIN",
            "email": "admin@test.com",
        }

        mock_decode.return_value = payload

        user, returned_payload = self.authentication.authenticate(self.request)

        assert user.id == "123"
        assert user.role == "ADMIN"
        assert user.email == "admin@test.com"
        assert returned_payload == payload
