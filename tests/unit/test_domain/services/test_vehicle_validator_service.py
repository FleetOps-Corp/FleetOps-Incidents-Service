"""Unit tests for VehicleValidatorService."""

import pytest

from incidents.domain.exceptions import VehicleNotRegisteredException


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
        vehicle_validator_service.validate_vehicle_exists(placa, authorization="Bearer token")

        mock_vehicle_client.validate_plate_exists.assert_called_once_with(placa=placa, authorization="Bearer token")

    def test_validate_vehicle_not_exists(
        self, vehicle_validator_service, mock_vehicle_client
    ):
        """Given: Invalid plate, When: Validate, Then: Raise exception."""
        # Arrange
        placa = "FAKE-999"
        mock_vehicle_client.validate_plate_exists.return_value = False

        # Act & Assert
        with pytest.raises(VehicleNotRegisteredException) as exc_info:
            vehicle_validator_service.validate_vehicle_exists(placa, authorization="Bearer token")

        assert "not registered" in str(exc_info.value.message)

    def test_validate_vehicle_client_error(
        self, vehicle_validator_service, mock_vehicle_client
    ):
        """Given: Client error, When: Validate, Then: Raise VehicleNotRegisteredException."""
        # Arrange
        placa = "ABC-124"
        mock_vehicle_client.validate_plate_exists.side_effect = Exception(
            "Network error"
        )

        # Act & Assert
        with pytest.raises(VehicleNotRegisteredException):
            vehicle_validator_service.validate_vehicle_exists(placa, authorization="Bearer token")
