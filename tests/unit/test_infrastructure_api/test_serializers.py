from incidents.infrastructure.api.serializers import (
    IncidentQuerySerializer,
    IncidentRequestSerializer,
)

BASE_VALID = {
    "driver_id": "driver-123",
    "vehicle_id": "ABC123",
    "incident_type": "HUMANO",
    "severity": "LEVE",
    "description": "Some event",
    "event_date": "2024-01-01T00:00:00Z",
}


def test_vehicle_id_is_uppercased_and_stripped():
    data = BASE_VALID.copy()
    data["vehicle_id"] = "  abC123  "
    ser = IncidentRequestSerializer(data=data)
    assert ser.is_valid(), ser.errors
    assert ser.validated_data["vehicle_id"] == "ABC123"


def test_driver_id_whitespace_is_invalid():
    data = BASE_VALID.copy()
    data["driver_id"] = "   "
    ser = IncidentRequestSerializer(data=data)
    assert not ser.is_valid()
    assert "driver_id" in ser.errors
    # field-level validator may be bypassed by the field blank check; accept
    # either the custom message or the built-in blank-field message.
    err = str(ser.errors["driver_id"][0]).lower()
    assert "conductor id" in err or "blank" in err or "no puede" in err


def test_missing_required_fields_fails():
    data = BASE_VALID.copy()
    del data["description"]
    ser = IncidentRequestSerializer(data=data)
    assert not ser.is_valid()
    assert "description" in ser.errors


def test_query_serializer_accepts_empty_and_parses_dates():
    ser = IncidentQuerySerializer(data={})
    assert ser.is_valid(), ser.errors

    ser = IncidentQuerySerializer(data={"start_date": "2024-01-01T00:00:00Z"})
    assert ser.is_valid(), ser.errors
    assert "start_date" in ser.validated_data
