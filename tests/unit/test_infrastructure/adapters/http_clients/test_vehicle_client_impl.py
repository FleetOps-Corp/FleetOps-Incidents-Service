"""Unit tests for Vehicle HTTP client adapter with Circuit Breaker."""

import pytest
from unittest.mock import Mock, patch

from incidents.infrastructure.adapters.http_clients.vehicle_client_impl import (
    VehicleClientWithCircuitBreaker,
)
from incidents.domain.exceptions import VehicleNotRegisteredException


class TestVehicleClientWithCircuitBreaker:
    """Test Vehicle client adapter with Circuit Breaker pattern."""

    @pytest.fixture
    def client(self):
        """Create client instance."""
        return VehicleClientWithCircuitBreaker(
            vehicles_api_url="http://localhost:8000",
            timeout_seconds=5.0,
            fail_max=5,
            reset_timeout=60,
        )

    @patch("incidents.infrastructure.adapters.http_clients.vehicle_client_impl.requests.get")
    def test_validate_plate_exists_success(self, mock_get, client):
        """Given: Valid plate, When: Validate, Then: Return True."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Act
        result = client.validate_plate_exists("ABC-1234")

        # Assert
        assert result is True

    @patch("incidents.infrastructure.adapters.http_clients.vehicle_client_impl.requests.get")
    def test_validate_plate_not_found(self, mock_get, client):
        """Given: Nonexistent plate, When: Validate, Then: Return False."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = client.validate_plate_exists("FAKE-9999")

        assert result is False

    def test_validate_plate_connection_error(self, client):
        """Given: Connection error, When: Validate, Then: Raise VehicleNotRegisteredException."""
        with patch("incidents.infrastructure.adapters.http_clients.vehicle_client_impl.requests.get") as mock_get:
            mock_get.side_effect = Exception("Connection refused")

            with pytest.raises(VehicleNotRegisteredException):
                client.validate_plate_exists("ABC-1234")

    @patch("incidents.infrastructure.adapters.http_clients.vehicle_client_impl.requests.get")
    def test_get_vehicle_details_success(self, mock_get, client):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"plate": "ABC-1234"}
        mock_get.return_value = mock_response

        result = client.get_vehicle_details("ABC-1234")

        assert result == {"plate": "ABC-1234"}

    @patch("incidents.infrastructure.adapters.http_clients.vehicle_client_impl.requests.get")
    def test_get_vehicle_details_not_found(self, mock_get, client):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = client.get_vehicle_details("ABC-1234")

        assert result is None

    @patch("incidents.infrastructure.adapters.http_clients.vehicle_client_impl.requests.get")
    def test_get_vehicle_details_exception_returns_none(self, mock_get, client):
        mock_get.side_effect = Exception("Connection refused")

        result = client.get_vehicle_details("ABC-1234")

        assert result is None

    def test_breaker_listener_methods(self, client):
        listener = client._breaker_listener()

        listener.before_call(None, None)
        listener.state_change(None, "closed", "open")
        listener.failure(None, Exception("boom"))
        listener.success(None)
