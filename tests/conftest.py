"""Test configuration and fixtures."""

import pytest
from unittest.mock import Mock, MagicMock
from incidents.domain.ports import IncidentRepository, MessageBrokerPort, VehicleClientPort
from incidents.domain.services import IncidentService, VehicleValidatorService
from incidents.application.use_cases import (
    RegisterIncidentUseCase,
    QueryIncidentsUseCase,
)


@pytest.fixture
def mock_incident_repository():
    """Fixture: Mock incident repository."""
    return Mock(spec=IncidentRepository)


@pytest.fixture
def mock_message_broker():
    """Fixture: Mock message broker."""
    return Mock(spec=MessageBrokerPort)


@pytest.fixture
def mock_vehicle_client():
    """Fixture: Mock vehicle client."""
    return Mock(spec=VehicleClientPort)


@pytest.fixture
def incident_service(mock_incident_repository, mock_message_broker):
    """Fixture: Incident domain service with mocked adapters."""
    return IncidentService(mock_incident_repository, mock_message_broker)


@pytest.fixture
def vehicle_validator_service(mock_vehicle_client):
    """Fixture: Vehicle validator service with mocked client."""
    return VehicleValidatorService(mock_vehicle_client)


@pytest.fixture
def register_incident_use_case(incident_service, vehicle_validator_service):
    """Fixture: Register incident use case."""
    return RegisterIncidentUseCase(incident_service, vehicle_validator_service)


@pytest.fixture
def query_incidents_use_case(incident_service):
    """Fixture: Query incidents use case."""
    return QueryIncidentsUseCase(incident_service)
