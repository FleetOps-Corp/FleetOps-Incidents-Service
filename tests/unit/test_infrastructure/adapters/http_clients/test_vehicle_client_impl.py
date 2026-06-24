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
