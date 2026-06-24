"""Unit tests for DjangoIncidentRepository adapter."""

import pytest
from datetime import datetime
from uuid import uuid4
from unittest.mock import patch, MagicMock

from incidents.domain.models import Incident, IncidentType, IncidentSeverity, PlateNumber
from incidents.infrastructure.adapters.persistence.incident_repository import DjangoIncidentRepository


class TestDjangoIncidentRepository:
    """Test repository adapter for Django ORM."""

    @pytest.fixture
    def repository(self):
        """Create repository instance."""
        return DjangoIncidentRepository()

    def test_orm_to_domain_conversion(self, repository):
        """Given: ORM model, When: Convert to domain, Then: Correct mapping."""
        # Arrange
        orm_incident = MagicMock()
        orm_incident.id = uuid4()
        orm_incident.fecha_hora = datetime.utcnow()
        orm_incident.id_conductor = "conductor-123"
        orm_incident.placa_vehiculo = "ABC-1234"
        orm_incident.tipo_incidente = "MECANICO"
        orm_incident.gravedad = "GRAVE"
        orm_incident.descripcion = "Engine failure"
        orm_incident.estado = "REGISTRADO"
        orm_incident.created_at = datetime.utcnow()
        orm_incident.updated_at = datetime.utcnow()

        # Act
        domain_incident = repository._orm_to_domain(orm_incident)

        # Assert
        assert domain_incident.id_conductor == "conductor-123"
        assert domain_incident.get_plate_str() == "ABC-1234"
        assert domain_incident.tipo_incidente == IncidentType.MECANICO
        assert domain_incident.gravedad == IncidentSeverity.GRAVE
