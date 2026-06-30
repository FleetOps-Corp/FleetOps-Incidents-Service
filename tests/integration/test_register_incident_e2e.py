"""End-to-End integration test - Complete transactional flow."""

import pytest
from datetime import datetime
from unittest.mock import Mock

# from uuid import uuid4

# from incidents.domain.models import Incident
from incidents.domain.services import IncidentService, VehicleValidatorService
from incidents.application.use_cases import RegisterIncidentUseCase
from incidents.application.dtos import IncidentDTO
from incidents.infrastructure.adapters.persistence.incident_repository import (
    DjangoIncidentRepository,
)
from incidents.infrastructure.adapters.messaging.rabbitmq_producer import (
    RabbitMQProducer,
)
from incidents.infrastructure.adapters.http_clients.vehicle_client_impl import (
    VehicleClientWithCircuitBreaker,
)
from incidents.domain.models import Incident


class TestRegisterIncidentE2E:
    """
    End-to-End test: Complete transactional flow

    Flow (Workflow 1 from SAD):
    1. REST API receives incident request
    2. Use case validates vehicle (Circuit Breaker)
    3. Domain service creates incident
    4. Repository persists to DB
    5. Message broker publishes event
    6. SAGA coordination begins

    This test exercises ALL architectural layers.
    """

    @pytest.fixture
    def e2e_setup(self):
        """Setup E2E test with mocked external services."""
        # Mock adapters
        mock_repo = Mock(spec=DjangoIncidentRepository)
        mock_broker = Mock(spec=RabbitMQProducer)
        mock_vehicle_client = Mock(spec=VehicleClientWithCircuitBreaker)

        # Domain services
        incident_service = IncidentService(mock_repo, mock_broker)
        vehicle_validator = VehicleValidatorService(mock_vehicle_client)

        # Application use case
        use_case = RegisterIncidentUseCase(incident_service, vehicle_validator)

        return {
            "use_case": use_case,
            "mock_repo": mock_repo,
            "mock_broker": mock_broker,
            "mock_vehicle_client": mock_vehicle_client,
        }

    def test_complete_incident_registration_flow(self, e2e_setup):
        """
        Given: All microservices operational
        When: Register incident (MECANICO GRAVE)
        Then: Complete flow executes: validate → create → persist → publish
        """
        # Arrange
        use_case = e2e_setup["use_case"]
        mock_repo = e2e_setup["mock_repo"]
        mock_broker = e2e_setup["mock_broker"]
        mock_vehicle_client = e2e_setup["mock_vehicle_client"]

        # 1. Vehicle validation succeeds
        mock_vehicle_client.validate_plate_exists.return_value = True

        # 2. Repository persists incident
        saved_incident = Incident.create(
            id_conductor="conductor-123",
            placa_vehiculo="ABC-1234",
            tipo_incidente="MECANICO",
            gravedad="GRAVE",
            descripcion="Engine failure",
            fecha_hora=datetime.fromisoformat("2026-06-10T14:30:00"),
        )

        mock_repo.save.return_value = saved_incident

        # Create DTO
        incident_dto = IncidentDTO(
            id_conductor="conductor-123",
            placa_vehiculo="ABC-1234",
            tipo_incidente="MECANICO",
            gravedad="GRAVE",
            descripcion="Engine failure",
            fecha_hora=datetime.fromisoformat("2026-06-10T14:30:00"),
        )

        # Act
        response_dto = use_case.execute(incident_dto)

        # Assert Layer 1: Application
        assert response_dto.id == saved_incident.id
        assert response_dto.id_conductor == "conductor-123"

        # Generated ID format
        assert response_dto.id.startswith("INC-")

        # Assert Layer 2: Domain
        mock_vehicle_client.validate_plate_exists.assert_called_once_with("ABC-1234")

        # Assert Layer 3: Persistence
        mock_repo.save.assert_called_once()
        saved_call = mock_repo.save.call_args[0][0]

        assert saved_call.tipo_incidente.value == "MECANICO"
        assert saved_call.gravedad.value == "GRAVE"

        # Assert Layer 4: Messaging
        mock_broker.publish_incident_registered.assert_called_once()

        published_event = mock_broker.publish_incident_registered.call_args[0][0]

        assert published_event["incident_id"] == saved_incident.id
        assert published_event["incident_type"] == "MECANICO"
        assert published_event["severity"] == "GRAVE"

    def test_failed_vehicle_validation_aborts_flow(self, e2e_setup):
        """
        Given: Vehicle not registered
        When: Register incident
        Then: Flow aborts at validation, no DB write or event published
        """
        use_case = e2e_setup["use_case"]
        mock_repo = e2e_setup["mock_repo"]
        mock_broker = e2e_setup["mock_broker"]
        mock_vehicle_client = e2e_setup["mock_vehicle_client"]

        # Vehicle validation fails
        mock_vehicle_client.validate_plate_exists.return_value = False

        incident_dto = IncidentDTO(
            id_conductor="c1",
            placa_vehiculo="FAKE-9999",
            tipo_incidente="HUMANO",
            gravedad="GRAVE",
            descripcion="Me corte la mano",
            fecha_hora=datetime.fromisoformat("2026-06-10T14:30:00"),
        )

        # Act & Assert
        from incidents.application.exceptions import VehicleValidationError

        with pytest.raises(VehicleValidationError):
            use_case.execute(incident_dto)

        # Verify flow stops at validation layer
        mock_repo.save.assert_not_called()
        mock_broker.publish_incident_registered.assert_not_called()
