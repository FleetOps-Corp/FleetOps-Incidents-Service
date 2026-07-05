"""Unit tests for REST API serializers."""

from incidents.infrastructure.api.serializers import (
    IncidentQuerySerializer,
    IncidentRequestSerializer,
    IncidentResponseSerializer,
)


class TestIncidentRequestSerializer:
    def test_valid_request_normalizes_vehicle_id(self):
        serializer = IncidentRequestSerializer(
            data={
                "driver_id": "driver-123",
                "vehicle_id": " abc-1234 ",
                "incident_type": "MECANICO",
                "severity": "GRAVE",
                "description": "Engine failure",
                "event_date": "2026-06-10T14:30:00Z",
            }
        )

        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data["vehicle_id"] == "ABC-1234"
        assert serializer.validated_data["driver_id"] == "driver-123"

    def test_invalid_driver_id_rejected(self):
        serializer = IncidentRequestSerializer(
            data={
                "driver_id": "   ",
                "vehicle_id": "ABC-1234",
                "incident_type": "MECANICO",
                "severity": "GRAVE",
                "description": "Engine failure",
                "event_date": "2026-06-10T14:30:00Z",
            }
        )

        assert not serializer.is_valid()
        assert "driver_id" in serializer.errors

    def test_invalid_incident_type_rejected(self):
        serializer = IncidentRequestSerializer(
            data={
                "driver_id": "driver-123",
                "vehicle_id": "ABC-1234",
                "incident_type": "INVALID",
                "severity": "GRAVE",
                "description": "Engine failure",
                "event_date": "2026-06-10T14:30:00Z",
            }
        )

        assert not serializer.is_valid()
        assert "incident_type" in serializer.errors


class TestIncidentQuerySerializer:
    def test_query_serializer_accepts_filters(self):
        serializer = IncidentQuerySerializer(
            data={
                "incident_type": "HUMANO",
                "severity": "LEVE",
                "vehicle_id": "ABC-1234",
                "driver_id": "driver-123",
                "start_date": "2026-06-10T14:30:00Z",
                "end_date": "2026-06-10T15:30:00Z",
            }
        )

        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data["incident_type"] == "HUMANO"
        assert serializer.validated_data["start_date"].tzinfo is not None


class TestIncidentResponseSerializer:
    def test_response_serializer_passthrough(self):
        serializer = IncidentResponseSerializer(
            {
                "incident_id": "1",
                "event_date": "2026-06-10T14:30:00",
                "driver_id": "driver-123",
                "vehicle_id": "ABC-1234",
                "incident_type": "MECANICO",
                "severity": "GRAVE",
                "description": "Engine failure",
                "created_at": "2026-06-10T14:30:00",
                "updated_at": "2026-06-10T14:30:00",
            }
        )

        assert serializer.data["vehicle_id"] == "ABC-1234"
