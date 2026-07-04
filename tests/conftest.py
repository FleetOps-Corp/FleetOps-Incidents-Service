"""Test configuration and fixtures."""

from unittest.mock import Mock

import pytest

from incidents.application.use_cases import (
    QueryIncidentsUseCase,
    RegisterIncidentUseCase,
)
from incidents.domain.ports import (
    IncidentRepository,
    MessagePublisherPort,
    VehicleClientPort,
)
from incidents.domain.services import IncidentService, VehicleValidatorService


@pytest.fixture
def mock_incident_repository():
    """Fixture: Mock incident repository."""
    return Mock(spec=IncidentRepository)


@pytest.fixture
def mock_message_publisher():
    """Fixture: Mock message publisher."""
    return Mock(spec=MessagePublisherPort)


@pytest.fixture
def mock_vehicle_client():
    """Fixture: Mock vehicle client."""
    return Mock(spec=VehicleClientPort)


@pytest.fixture
def incident_service(mock_incident_repository, mock_message_publisher):
    """Fixture: Incident domain service with mocked adapters."""
    return IncidentService(mock_incident_repository, mock_message_publisher)


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
