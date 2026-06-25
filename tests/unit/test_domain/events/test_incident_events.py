"""Unit tests for domain events."""

from datetime import datetime
from uuid import uuid4

from incidents.domain.events import IncidentRegisteredEvent


class TestIncidentRegisteredEvent:
    """Test IncidentRegisteredEvent."""

    def test_event_creation(self):
        """Given: Event data, When: Create event, Then: Fields set correctly."""
        incident_id = uuid4()
        event = IncidentRegisteredEvent(
            incident_id=incident_id,
            id_conductor="conductor-123",
            placa_vehiculo="ABC-1234",
            tipo_incidente="MECANICO",
            gravedad="GRAVE",
            descripcion="Engine failure",
            fecha_evento=datetime.utcnow(),
        )

        assert event.incident_id == incident_id
        assert event.id_conductor == "conductor-123"
        assert event.tipo_incidente == "MECANICO"

    def test_event_to_dict(self):
        """Given: Event, When: Convert to dict, Then: JSON serializable."""
        incident_id = uuid4()
        now = datetime.utcnow()
        event = IncidentRegisteredEvent(
            incident_id=incident_id,
            id_conductor="c1",
            placa_vehiculo="ABC",
            tipo_incidente="HUMANO",
            gravedad="GRAVE",
            descripcion="Test",
            fecha_evento=now,
        )

        result = event.to_dict()

        assert result["event_type"] == "incident.registered"
        assert result["incident_id"] == str(incident_id)
        assert result["id_conductor"] == "c1"
