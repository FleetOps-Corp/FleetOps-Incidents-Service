"""Unit tests for REST API views."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from incidents.application.dtos import IncidentResponseDTO
from incidents.application.exceptions import (
    ApplicationException,
    VehicleValidationError,
)
from incidents.domain.exceptions import DomainException
from incidents.infrastructure.api import views


class TestCreateIncidentView:
    """Test POST /api/incidents/ endpoint."""

    @pytest.fixture
    def factory(self):
        """Create request factory."""
        return APIRequestFactory()

    @pytest.fixture
    def user(self):
        """Authenticated mock user."""
        return SimpleNamespace(
            is_authenticated=True,
            role="ADMINISTRADOR",
            id="user-1",
            email="test@test.com",
        )

    @pytest.fixture(autouse=True)
    def setup_use_cases(self):
        """Setup mock use cases for views."""
        register_uc = Mock()
        query_uc = Mock()
        views.set_use_cases(register_uc, query_uc)
        yield register_uc, query_uc

    # Fails bc id is generated in other way
    def test_create_incident_success(self, factory, user):
        """Given: Valid incident data, When: POST, Then: Return 201."""
        # Arrange
        request_data = {
            "driver_id": "conductor-123",
            "vehicle_id": "ABC-1234",
            "incident_type": "MECANICO",
            "severity": "GRAVE",
            "description": "Engine failure",
            "event_date": "2026-06-10T14:30:00Z",
        }

        response_dto = IncidentResponseDTO(
            incident_id="550e8400-e29b-41d4-a716-446655440000",
            event_date="2026-06-10T14:30:00",
            driver_id="conductor-123",
            vehicle_id="ABC-1234",
            incident_type="MECANICO",
            severity="GRAVE",
            description="Engine failure",
            created_at="2026-06-10T14:30:00",
            updated_at="2026-06-10T14:30:00",
        )

        views.register_incident_uc.execute.return_value = response_dto

        # request = factory.post("/api/incidents/", request_data, format="json")
        # request.user = Mock(is_authenticated=True)

        request = factory.post("/api/incidents/", request_data, format="json")
        force_authenticate(request, user=user)
        force_authenticate(request, user=user)  # Forzar el pase de autenticación de DRF

        # Act
        response = views.create_incident(request)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_incident_invalid_data(self, factory, user):
        """Given: Invalid data, When: POST, Then: Return 400."""
        request_data = {
            "driver_id": "",  # Empty
            "vehicle_id": "ABC-1234",
            "incident_type": "MECANICO",
            "severity": "GRAVE",
            "description": "Engine failure",
            "event_date": "2026-06-10T14:30:00Z",
        }

        request = factory.post("/api/incidents/", request_data, format="json")
        force_authenticate(request, user=user)
        force_authenticate(request, user=user)  # Forzar el pase de autenticación de DRF

        response = views.create_incident(request)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_incident_vehicle_validation_error(self, factory, user):
        request_data = {
            "driver_id": "conductor-123",
            "vehicle_id": "ABC-1234",
            "incident_type": "MECANICO",
            "severity": "GRAVE",
            "description": "Engine failure",
            "event_date": "2026-06-10T14:30:00Z",
        }

        views.register_incident_uc.execute.side_effect = VehicleValidationError(
            "vehicle missing"
        )
        request = factory.post("/api/incidents/", request_data, format="json")
        force_authenticate(request, user=user)

        response = views.create_incident(request)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.data["code"] == "VEHICLE_NOT_REGISTERED"

    def test_create_incident_domain_exception(self, factory, user):
        request_data = {
            "driver_id": "conductor-123",
            "vehicle_id": "ABC-1234",
            "incident_type": "MECANICO",
            "severity": "GRAVE",
            "description": "Engine failure",
            "event_date": "2026-06-10T14:30:00Z",
        }

        views.register_incident_uc.execute.side_effect = DomainException(
            "invalid incident"
        )
        request = factory.post("/api/incidents/", request_data, format="json")
        force_authenticate(request, user=user)

        response = views.create_incident(request)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_incident_application_exception(self, factory, user):
        request_data = {
            "driver_id": "conductor-123",
            "vehicle_id": "ABC-1234",
            "incident_type": "MECANICO",
            "severity": "GRAVE",
            "description": "Engine failure",
            "event_date": "2026-06-10T14:30:00Z",
        }

        views.register_incident_uc.execute.side_effect = ApplicationException(
            "boom", code="APP_ERROR"
        )
        request = factory.post("/api/incidents/", request_data, format="json")
        force_authenticate(request, user=user)

        response = views.create_incident(request)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data["code"] == "APP_ERROR"

    def test_create_incident_unexpected_exception(self, factory, user):
        request_data = {
            "driver_id": "conductor-123",
            "vehicle_id": "ABC-1234",
            "incident_type": "MECANICO",
            "severity": "GRAVE",
            "description": "Engine failure",
            "event_date": "2026-06-10T14:30:00Z",
        }

        views.register_incident_uc.execute.side_effect = Exception("boom")
        request = factory.post("/api/incidents/", request_data, format="json")
        force_authenticate(request, user=user)

        response = views.create_incident(request)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data == {"error": "Internal server error"}

    def test_create_incident_without_use_case(self, factory, user):
        request_data = {
            "driver_id": "conductor-123",
            "vehicle_id": "ABC-1234",
            "incident_type": "MECANICO",
            "severity": "GRAVE",
            "description": "Engine failure",
            "event_date": "2026-06-10T14:30:00Z",
        }

        views.set_use_cases(None, None)
        request = factory.post("/api/incidents/", request_data, format="json")
        force_authenticate(request, user=user)

        response = views.create_incident(request)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_query_incidents_success(self, factory, user):
        views.query_incidents_uc.execute.return_value = [
            SimpleNamespace(
                to_dict=lambda: {
                    "id": "1",
                    "fecha_hora": "2026-06-10T14:30:00",
                    "id_conductor": "c1",
                    "placa_vehiculo": "ABC-1234",
                    "tipo_incidente": "MECANICO",
                    "gravedad": "GRAVE",
                    "descripcion": "Engine failure",
                    "created_at": "2026-06-10T14:30:00",
                    "updated_at": "2026-06-10T14:30:00",
                }
            )
        ]

        request = factory.get("/api/incidents/?incident_type=MECANICO")
        force_authenticate(request, user=user)
        response = views.query_incidents(request)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_query_incidents_invalid_data(self, factory, user):
        request = factory.get("/api/incidents/?incident_type=INVALID")
        force_authenticate(request, user=user)

        response = views.query_incidents(request)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_query_incidents_application_exception(self, factory, user):
        views.query_incidents_uc.execute.side_effect = ApplicationException(
            "boom", code="APP_ERROR"
        )
        request = factory.get("/api/incidents/?incident_type=MECANICO")
        force_authenticate(request, user=user)

        response = views.query_incidents(request)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_query_incidents_without_use_case(self, factory, user):
        views.set_use_cases(Mock(), None)
        request = factory.get("/api/incidents/")
        force_authenticate(request, user=user)

        response = views.query_incidents(request)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_get_incident_success(self, factory, user):
        dto = IncidentResponseDTO(
            incident_id="1",
            event_date="2026-06-10T14:30:00",
            driver_id="c1",
            vehicle_id="ABC-1234",
            incident_type="MECANICO",
            severity="GRAVE",
            description="Engine failure",
            created_at="2026-06-10T14:30:00",
            updated_at="2026-06-10T14:30:00",
        )
        views.query_incidents_uc.execute_by_id.return_value = dto

        request = factory.get("/api/incidents/1/")
        force_authenticate(request, user=user)
        response = views.get_incident(request, "1")

        assert response.status_code == status.HTTP_200_OK

    def test_get_incident_invalid_id(self, factory, user):
        views.query_incidents_uc.execute_by_id.side_effect = ValueError("bad id")

        request = factory.get("/api/incidents/bad/")
        force_authenticate(request, user=user)
        response = views.get_incident(request, "bad")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_incident_not_found(self, factory, user):
        views.query_incidents_uc.execute_by_id.side_effect = Exception("missing")

        request = factory.get("/api/incidents/1/")
        force_authenticate(request, user=user)
        response = views.get_incident(request, "1")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_incident_without_use_case(self, factory, user):
        views.set_use_cases(Mock(), None)

        request = factory.get("/api/incidents/1/")
        force_authenticate(request, user=user)
        response = views.get_incident(request, "1")

        assert response.status_code == status.HTTP_404_NOT_FOUND
