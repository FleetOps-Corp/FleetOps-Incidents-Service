"""Unit tests for RegisterIncidentUseCase."""

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from incidents.application.dtos import IncidentDTO
from incidents.application.exceptions import VehicleValidationError
from incidents.application.use_cases import RegisterIncidentUseCase
from incidents.domain.exceptions import DomainException, VehicleNotRegisteredException


class TestRegisterIncidentUseCase:
    def test_execute_success(self):
        incident_service = Mock()
        vehicle_validator = Mock()
        use_case = RegisterIncidentUseCase(incident_service, vehicle_validator)

        incident = SimpleNamespace(
            id="INC-20260601-abcd",
            fecha_hora=datetime(2026, 6, 1, 10, 30, 0),
            id_conductor="driver-1",
            get_plate_str=Mock(return_value="ABC-124"),
            tipo_incidente=SimpleNamespace(value="HUMANO"),
            gravedad=SimpleNamespace(value="GRAVE"),
            descripcion="Desc",
            created_at=datetime(2026, 6, 1, 10, 31, 0),
            updated_at=datetime(2026, 6, 1, 10, 32, 0),
        )
        incident_service.register_incident.return_value = incident

        dto = IncidentDTO(
            driver_id="driver-1",
            vehicle_id="ABC-124",
            incident_type="HUMANO",
            severity="GRAVE",
            description="Desc",
            event_date=datetime(2026, 6, 1, 10, 30, 0),
        )

        result = use_case.execute(dto, authorization="Bearer token")

        vehicle_validator.validate_vehicle_exists.assert_called_once_with("ABC-124", "Bearer token",)
        incident_service.register_incident.assert_called_once()
        assert result.incident_id == "INC-20260601-abcd"
        assert result.vehicle_id == "ABC-124"

    def test_execute_vehicle_not_registered_raises_application_error(self):
        incident_service = Mock()
        vehicle_validator = Mock()
        vehicle_validator.validate_vehicle_exists.side_effect = (
            VehicleNotRegisteredException("missing")
        )
        use_case = RegisterIncidentUseCase(incident_service, vehicle_validator)

        dto = IncidentDTO(
            driver_id="driver-1",
            vehicle_id="ABC-1234",
            incident_type="HUMANO",
            severity="GRAVE",
            description="Desc",
            event_date=datetime(2026, 6, 1, 10, 30, 0),
        )

        with pytest.raises(VehicleValidationError) as exc_info:
            use_case.execute(dto, authorization="Bearer token")

        assert "missing" in str(exc_info.value)
        incident_service.register_incident.assert_not_called()

    def test_execute_domain_exception_is_propagated(self):
        incident_service = Mock()
        incident_service.register_incident.side_effect = DomainException("invalid data")
        vehicle_validator = Mock()
        use_case = RegisterIncidentUseCase(incident_service, vehicle_validator)

        dto = IncidentDTO(
            driver_id="driver-1",
            vehicle_id="ABC-1234",
            incident_type="HUMANO",
            severity="GRAVE",
            description="Desc",
            event_date=datetime(2026, 6, 1, 10, 30, 0),
        )

        with pytest.raises(DomainException):
            use_case.execute(dto, authorization="Bearer token")
