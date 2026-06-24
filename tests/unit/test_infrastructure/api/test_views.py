"""Unit tests for REST API views."""

import pytest
from unittest.mock import Mock, patch
from rest_framework.test import APIRequestFactory
from rest_framework import status

from incidents.infrastructure.api import views
from incidents.application.dtos import IncidentResponseDTO
from rest_framework.test import force_authenticate



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

#Fails bc id is generated in other way
    def test_create_incident_success(self, factory):
        """Given: Valid incident data, When: POST, Then: Return 201."""
        # Arrange
        request_data = {
            "id_conductor": "conductor-123",
            "placa_vehiculo": "ABC-1234",
            "tipo_incidente": "MECANICO",
            "gravedad": "GRAVE",
            "descripcion": "Engine failure",
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
        }

        # request = factory.post("/api/incidents/", request_data, format="json")
        # request.user = Mock(is_authenticated=True)

        user = Mock()  # Crea un usuario ficticio
        request = factory.post("/api/incidents/", request_data, format="json")
        force_authenticate(request, user=user)  # Forzar el pase de autenticación de DRF
        
        response = views.create_incident(request)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
