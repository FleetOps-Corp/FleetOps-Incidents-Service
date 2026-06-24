"""Unit tests for RegisterIncidentUseCase."""

import pytest
from unittest.mock import Mock

from incidents.application.use_cases import RegisterIncidentUseCase
from incidents.application.dtos import IncidentDTO
from incidents.application.exceptions import VehicleValidationError
from incidents.domain.models import Incident
from incidents.domain.exceptions import VehicleNotRegisteredException, InvalidIncidentTypeException


class TestRegisterIncidentUseCase:
    """Test RegisterIncidentUseCase primary transactional flow."""

    def test_execute_success(self, register_incident_use_case, mock_vehicle_client, mock_incident_repository):
        """
        Given: Valid incident DTO and registered vehicle
        When: Execute use case
        Then: Incident created and response returned
        """
        # Arrange
        incident_dto = IncidentDTO(
            id_conductor="conductor-123",
            placa_vehiculo="ABC-1234",
            tipo_incidente="MECANICO",
            gravedad="GRAVE",
            descripcion="Engine failure",
        )

        mock_vehicle_client.validate_plate_exists.return_value = True

        saved_incident = Incident.create(
            id_conductor="conductor-123",
            placa_vehiculo="ABC-1234",
            tipo_incidente="MECANICO",
            gravedad="GRAVE",
            descripcion="Engine failure",
        )
        mock_incident_repository.save.return_value = saved_incident

        # Act
        result = register_incident_use_case.execute(incident_dto)

        # Assert
        assert result.id_conductor == "conductor-123"
        assert result.placa_vehiculo == "ABC-1234"
        assert result.tipo_incidente == "MECANICO"

    def test_execute_vehicle_not_registered(self, register_incident_use_case, mock_vehicle_client):
        """Given: Unregistered vehicle, When: Execute, Then: Raise VehicleValidationError."""
        # Arrange
        incident_dto = IncidentDTO(
            id_conductor="c1",
            placa_vehiculo="FAKE-9999",
            tipo_incidente="HUMANO",
            gravedad="GRAVE",
        )

        mock_vehicle_client.validate_plate_exists.return_value = False

        # Act & Assert
        with pytest.raises(VehicleValidationError):
            register_incident_use_case.execute(incident_dto)

    def test_execute_vehicle_validation_error(self, register_incident_use_case, mock_vehicle_client):
        """Given: Vehicle client throws error, When: Execute, Then: Raise VehicleValidationError."""
        incident_dto = IncidentDTO(
            id_conductor="c1",
            placa_vehiculo="ABC",
            tipo_incidente="HUMANO",
            gravedad="GRAVE",
        )

        mock_vehicle_client.validate_plate_exists.side_effect = VehicleNotRegisteredException("Network error")

        with pytest.raises(VehicleValidationError):
            register_incident_use_case.execute(incident_dto)

    def test_execute_invalid_incident_type(self, register_incident_use_case, mock_vehicle_client):
        """Given: Invalid type, When: Execute, Then: Raise DomainException."""
        incident_dto = IncidentDTO(
            id_conductor="c1",
            placa_vehiculo="ABC",
            tipo_incidente="INVALID_TYPE",
            gravedad="GRAVE",
        )

        mock_vehicle_client.validate_plate_exists.return_value = True

        with pytest.raises(InvalidIncidentTypeException):
            register_incident_use_case.execute(incident_dto)
