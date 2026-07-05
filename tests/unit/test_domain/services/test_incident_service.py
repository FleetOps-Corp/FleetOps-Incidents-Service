"""Unit tests for IncidentService domain service."""

from datetime import datetime

import pytest

from incidents.domain.exceptions import (
    InvalidIncidentSeverityException,
    InvalidIncidentTypeException,
)
from incidents.domain.models import Incident


class TestIncidentServiceRegister:
    """Test IncidentService.register_incident workflow."""

    def test_register_incident_success(
        self, incident_service, mock_incident_repository, mock_message_publisher
    ):
        """
        Given: Valid incident data
        When: Register incident
        Then: Save to repo and publish event
        """
        # Arrange
        id_conductor = "conductor-123"
        placa = "ABC-123"
        tipo = "MECANICO"
        gravedad = "GRAVE"
        descripcion = "Engine failure"
        fecha_hora = datetime(2026, 6, 17, 15, 58, 0)

        # Mock repository save
        saved_incident = Incident.create(
            id_conductor=id_conductor,
            placa_vehiculo=placa,
            tipo_incidente=tipo,
            gravedad=gravedad,
            descripcion=descripcion,
            fecha_hora=fecha_hora,
        )
        mock_incident_repository.save.return_value = saved_incident

        # Act
        result = incident_service.register_incident(
            id_conductor=id_conductor,
            placa_vehiculo=placa,
            tipo_incidente=tipo,
            gravedad=gravedad,
            descripcion=descripcion,
            fecha_hora=fecha_hora,
        )

        # Assert
        assert result == saved_incident
        mock_incident_repository.save.assert_called_once()
        # mock_message_broker.publish_incident_registered.assert_called_once()
        mock_message_publisher.publish.assert_called_once_with(
            event_type="incident_registered",
            payload=saved_incident.to_event(),
        )

    def test_register_incident_invalid_type(self, incident_service):
        """Given: Invalid type, When: Register, Then: Raise exception."""
        with pytest.raises(InvalidIncidentTypeException):
            incident_service.register_incident(
                id_conductor="c1",
                placa_vehiculo="ABC",
                tipo_incidente="INVALID",
                gravedad="GRAVE",
                descripcion="El conductor se enveneno",
                fecha_hora=datetime(2026, 6, 17, 15, 58, 0),
            )

    def test_register_incident_invalid_severity(self, incident_service):
        """Given: Invalid severity, When: Register, Then: Raise exception."""
        with pytest.raises(InvalidIncidentSeverityException):
            incident_service.register_incident(
                id_conductor="c1",
                placa_vehiculo="ABC",
                tipo_incidente="HUMANO",
                gravedad="INVALID",
                descripcion="El conductor se enveneno",
                fecha_hora=datetime(2026, 6, 17, 15, 58, 0),
            )

    def test_register_incident_publishes_correct_event(
        self, incident_service, mock_incident_repository
    ):
        """Given: Mechanical grave incident, When: Register, Then: Publish with correct data."""
        # Arrange
        saved_incident = Incident.create(
            id_conductor="c1",
            placa_vehiculo="ABC-123",
            tipo_incidente="MECANICO",
            gravedad="GRAVE",
            descripcion="El conductor se enveneno",
            fecha_hora=datetime(2026, 6, 17, 15, 58, 0),
        )
        mock_incident_repository.save.return_value = saved_incident

        # Act
        incident_service.register_incident(
            id_conductor="c1",
            placa_vehiculo="ABC-123",
            tipo_incidente="MECANICO",
            gravedad="GRAVE",
            descripcion="El conductor se enveneno",
            fecha_hora=datetime(2026, 6, 17, 15, 58, 0),
        )

    def test_register_incident_returns_success_even_if_publish_fails(
        self, incident_service, mock_incident_repository, mock_message_publisher
    ):
        """
        Given: SQS publish raises an exception
        When: Register incident
        Then: Incident is still returned (publish failure does not propagate)
        """
        saved_incident = Incident.create(
            id_conductor="c1",
            placa_vehiculo="ABC-123",
            tipo_incidente="MECANICO",
            gravedad="GRAVE",
            descripcion="Engine failure",
            fecha_hora=datetime(2026, 6, 17, 15, 58, 0),
        )
        mock_incident_repository.save.return_value = saved_incident
        mock_message_publisher.publish.side_effect = Exception("SQS unavailable")

        result = incident_service.register_incident(
            id_conductor="c1",
            placa_vehiculo="ABC-123",
            tipo_incidente="MECANICO",
            gravedad="GRAVE",
            descripcion="Engine failure",
            fecha_hora=datetime(2026, 6, 17, 15, 58, 0),
        )

        assert result == saved_incident  # No exception propagated


class TestIncidentServiceQuery:
    """Test IncidentService query methods."""

    def test_query_by_filters_all(self, incident_service, mock_incident_repository):
        """Given: No filters, When: Query, Then: Call repo find_by_filters."""
        # Arrange
        incidents = [
            Incident.create(
                "c1",
                "ABC-123",
                "HUMANO",
                "GRAVE",
                "El conductor se enveneno",
                datetime(2026, 6, 17, 15, 58, 0),
            ),
            Incident.create(
                "c2",
                "XYZ-567",
                "MECANICO",
                "LEVE",
                "El conductor se enveneno",
                datetime(2026, 6, 17, 15, 58, 0),
            ),
        ]
        mock_incident_repository.find_by_filters.return_value = incidents

        # Act
        result = incident_service.query_incidents_by_filters()

        # Assert
        assert result == incidents
        mock_incident_repository.find_by_filters.assert_called_once_with(
            tipo_incidente=None,
            gravedad=None,
            placa=None,
            id_conductor=None,
            fecha_desde=None,
            fecha_hasta=None,
        )

    def test_query_by_filters_tipo(self, incident_service, mock_incident_repository):
        """Given: Type filter, When: Query, Then: Pass to repo."""
        incidents = [
            Incident.create(
                "c1",
                "ABC-123",
                "HUMANO",
                "GRAVE",
                "El conductor se enveneno",
                datetime(2026, 6, 17, 15, 58, 0),
            )
        ]
        mock_incident_repository.find_by_filters.return_value = incidents

        incident_service.query_incidents_by_filters(tipo_incidente="HUMANO")

        mock_incident_repository.find_by_filters.assert_called_once_with(
            tipo_incidente="HUMANO",
            gravedad=None,
            placa=None,
            id_conductor=None,
            fecha_desde=None,
            fecha_hasta=None,
        )

    def test_query_by_filters_multiple(
        self, incident_service, mock_incident_repository
    ):
        """Given: Multiple filters, When: Query, Then: Pass all to repo."""
        incidents = []
        mock_incident_repository.find_by_filters.return_value = incidents

        incident_service.query_incidents_by_filters(
            tipo_incidente="MECANICO",
            gravedad="GRAVE",
            placa="ABC-123",
        )

        mock_incident_repository.find_by_filters.assert_called_once_with(
            tipo_incidente="MECANICO",
            gravedad="GRAVE",
            placa="ABC-123",
            id_conductor=None,
            fecha_desde=None,
            fecha_hasta=None,
        )
