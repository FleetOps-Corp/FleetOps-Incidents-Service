"""Unit tests for VehicleValidatorService."""

import pytest

from incidents.domain.exceptions import (
    VehicleNotRegisteredException,
    VehicleServiceAuthenticationException,
    VehicleServiceUnavailableException,
)


class TestVehicleValidatorService:
    """Test VehicleValidatorService validation logic."""

    def test_validate_vehicle_exists_success(
        self, vehicle_validator_service, mock_vehicle_client
    ):
        """Given: Valid plate, When: Validate, Then: Success."""
        # Arrange
        placa = "ABC-124"
        mock_vehicle_client.validate_plate_exists.return_value = True

        # Act & Assert (no exception)
        vehicle_validator_service.validate_vehicle_exists(
            placa, authorization="Bearer token"
        )

        mock_vehicle_client.validate_plate_exists.assert_called_once_with(
            placa=placa, authorization="Bearer token"
        )

    def test_validate_vehicle_not_exists(
        self, vehicle_validator_service, mock_vehicle_client
    ):
        """Given: Invalid plate, When: Validate, Then: Raise VehicleNotRegisteredException."""
        # Arrange
        placa = "FAKE-999"
        mock_vehicle_client.validate_plate_exists.side_effect = (
            VehicleNotRegisteredException("not registered")
        )

        # Act & Assert
        with pytest.raises(VehicleNotRegisteredException) as exc_info:
            vehicle_validator_service.validate_vehicle_exists(
                placa, authorization="Bearer token"
            )

        assert "not registered" in str(exc_info.value.message)

    def test_validate_vehicle_auth_error(
        self, vehicle_validator_service, mock_vehicle_client
    ):
        """Given: Auth error, When: Validate, Then: Raise VehicleServiceAuthenticationException."""
        # Arrange
        placa = "ABC-124"
        mock_vehicle_client.validate_plate_exists.side_effect = (
            VehicleServiceAuthenticationException("Auth failed")
        )

        # Act & Assert
        with pytest.raises(VehicleServiceAuthenticationException):
            vehicle_validator_service.validate_vehicle_exists(
                placa, authorization="invalid-token"
            )

    def test_validate_vehicle_service_unavailable(
        self, vehicle_validator_service, mock_vehicle_client
    ):
        """Given: Service unavailable, When: Validate, Then: Raise VehicleServiceUnavailableException."""
        # Arrange
        placa = "ABC-124"
        mock_vehicle_client.validate_plate_exists.side_effect = (
            VehicleServiceUnavailableException("Service down")
        )

        # Act & Assert
        with pytest.raises(VehicleServiceUnavailableException):
            vehicle_validator_service.validate_vehicle_exists(
                placa, authorization="Bearer token"
            )

    def test_validate_vehicle_unexpected_error(
        self, vehicle_validator_service, mock_vehicle_client
    ):
        """Given: Unexpected error, When: Validate, Then: Raise VehicleServiceUnavailableException."""
        # Arrange
        placa = "ABC-124"
        mock_vehicle_client.validate_plate_exists.side_effect = Exception(
            "Network error"
        )

        # Act & Assert
        with pytest.raises(VehicleServiceUnavailableException):
            vehicle_validator_service.validate_vehicle_exists(
                placa, authorization="Bearer token"
            )
