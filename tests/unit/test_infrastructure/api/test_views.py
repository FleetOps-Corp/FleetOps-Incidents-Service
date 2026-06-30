"""Unit tests for REST API views."""

import pytest
from types import SimpleNamespace
from unittest.mock import Mock

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

    @pytest.fixture(autouse=True)
    def setup_use_cases(self):
        """Setup mock use cases for views."""
        register_uc = Mock()
        query_uc = Mock()
        views.set_use_cases(register_uc, query_uc)
        yield register_uc, query_uc

    # Fails bc id is generated in other way
    def test_create_incident_success(self, factory):
        """Given: Valid incident data, When: POST, Then: Return 201."""
        # Arrange
        request_data = {
            "id_conductor": "conductor-123",
            "placa_vehiculo": "ABC-1234",
            "tipo_incidente": "MECANICO",
            "gravedad": "GRAVE",
            "descripcion": "Engine failure",
            "fecha_hora": "2026-06-10T14:30:00Z",
        }

        response_dto = IncidentResponseDTO(
            id="550e8400-e29b-41d4-a716-446655440000",
            fecha_hora="2026-06-10T14:30:00",
            id_conductor="conductor-123",
            placa_vehiculo="ABC-1234",
            tipo_incidente="MECANICO",
            gravedad="GRAVE",
            descripcion="Engine failure",
            # estado="REGISTRADO",
            created_at="2026-06-10T14:30:00",
            updated_at="2026-06-10T14:30:00",
        )

        views.register_incident_uc.execute.return_value = response_dto

        # request = factory.post("/api/incidents/", request_data, format="json")
        # request.user = Mock(is_authenticated=True)

        user = Mock()  # Crea un usuario ficticio
        request = factory.post("/api/incidents/", request_data, format="json")
        force_authenticate(request, user=user)  # Forzar el pase de autenticación de DRF

        # Act
        response = views.create_incident(request)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_incident_invalid_data(self, factory):
        """Given: Invalid data, When: POST, Then: Return 400."""
        request_data = {
            "id_conductor": "",  # Empty
            "placa_vehiculo": "ABC-1234",
            "tipo_incidente": "MECANICO",
            "gravedad": "GRAVE",
            "descripcion": "Engine failure",
            "fecha_hora": "2026-06-10T14:30:00Z",
        }

        # request = factory.post("/api/incidents/", request_data, format="json")
        # request.user = Mock(is_authenticated=True)

        user = Mock()  # Crea un usuario ficticio
        request = factory.post("/api/incidents/", request_data, format="json")
        force_authenticate(request, user=user)  # Forzar el pase de autenticación de DRF

        response = views.create_incident(request)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_incident_vehicle_validation_error(self, factory):
        request_data = {
            "id_conductor": "conductor-123",
            "placa_vehiculo": "ABC-1234",
            "tipo_incidente": "MECANICO",
            "gravedad": "GRAVE",
            "descripcion": "Engine failure",
            "fecha_hora": "2026-06-10T14:30:00Z",
        }

        views.register_incident_uc.execute.side_effect = VehicleValidationError(
            "vehicle missing"
        )
        request = factory.post("/api/incidents/", request_data, format="json")

        response = views.create_incident(request)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.data["code"] == "VEHICLE_NOT_REGISTERED"

    def test_create_incident_domain_exception(self, factory):
        request_data = {
            "id_conductor": "conductor-123",
            "placa_vehiculo": "ABC-1234",
            "tipo_incidente": "MECANICO",
            "gravedad": "GRAVE",
            "descripcion": "Engine failure",
            "fecha_hora": "2026-06-10T14:30:00Z",
        }

        views.register_incident_uc.execute.side_effect = DomainException(
            "invalid incident"
        )
        request = factory.post("/api/incidents/", request_data, format="json")

        response = views.create_incident(request)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_incident_application_exception(self, factory):
        request_data = {
            "id_conductor": "conductor-123",
            "placa_vehiculo": "ABC-1234",
            "tipo_incidente": "MECANICO",
            "gravedad": "GRAVE",
            "descripcion": "Engine failure",
            "fecha_hora": "2026-06-10T14:30:00Z",
        }

        views.register_incident_uc.execute.side_effect = ApplicationException(
            "boom", code="APP_ERROR"
        )
        request = factory.post("/api/incidents/", request_data, format="json")

        response = views.create_incident(request)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data["code"] == "APP_ERROR"

    def test_create_incident_unexpected_exception(self, factory):
        request_data = {
            "id_conductor": "conductor-123",
            "placa_vehiculo": "ABC-1234",
            "tipo_incidente": "MECANICO",
            "gravedad": "GRAVE",
            "descripcion": "Engine failure",
            "fecha_hora": "2026-06-10T14:30:00Z",
        }

        views.register_incident_uc.execute.side_effect = Exception("boom")
        request = factory.post("/api/incidents/", request_data, format="json")

        response = views.create_incident(request)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data == {"error": "Internal server error"}

    def test_query_incidents_success(self, factory):
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

        request = factory.get("/api/incidents/?tipo_incidente=MECANICO")
        response = views.query_incidents(request)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_query_incidents_invalid_data(self, factory):
        request = factory.get("/api/incidents/?tipo_incidente=INVALID")

        response = views.query_incidents(request)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_query_incidents_application_exception(self, factory):
        views.query_incidents_uc.execute.side_effect = ApplicationException(
            "boom", code="APP_ERROR"
        )
        request = factory.get("/api/incidents/?tipo_incidente=MECANICO")

        response = views.query_incidents(request)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_get_incident_success(self, factory):
        dto = IncidentResponseDTO(
            id="1",
            fecha_hora="2026-06-10T14:30:00",
            id_conductor="c1",
            placa_vehiculo="ABC-1234",
            tipo_incidente="MECANICO",
            gravedad="GRAVE",
            descripcion="Engine failure",
            created_at="2026-06-10T14:30:00",
            updated_at="2026-06-10T14:30:00",
        )
        views.query_incidents_uc.execute_by_id.return_value = dto

        request = factory.get("/api/incidents/1/")
        response = views.get_incident(request, "1")

        assert response.status_code == status.HTTP_200_OK

    def test_get_incident_invalid_id(self, factory):
        views.query_incidents_uc.execute_by_id.side_effect = ValueError("bad id")

        request = factory.get("/api/incidents/bad/")
        response = views.get_incident(request, "bad")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_incident_not_found(self, factory):
        views.query_incidents_uc.execute_by_id.side_effect = Exception("missing")

        request = factory.get("/api/incidents/1/")
        response = views.get_incident(request, "1")

        assert response.status_code == status.HTTP_404_NOT_FOUND
