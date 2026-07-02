"""REST API Serializers - Conversion between JSON and domain models."""

from rest_framework import serializers


class IncidentRequestSerializer(serializers.Serializer):
    """Deserializer for incident creation requests."""

    driver_id = serializers.CharField(max_length=255, required=True, allow_blank=False)
    vehicle_id = serializers.CharField(max_length=20)
    incident_type = serializers.ChoiceField(choices=["HUMANO", "MECANICO"])
    severity = serializers.ChoiceField(choices=["LEVE", "GRAVE"])
    description = serializers.CharField(required=True, allow_blank=False)
    event_date = serializers.DateTimeField(required=True)

    def validate_driver_id(self, value):
        """Validate conductor ID format."""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Conductor ID cannot be empty")
        return value

    def validate_vehicle_id(self, value):
        """Validate plate format."""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Plate number cannot be empty")
        return value.upper().strip()


class IncidentResponseSerializer(serializers.Serializer):
    """Serializer for incident responses."""

    incident_id = serializers.CharField()
    event_date = serializers.CharField()
    driver_id = serializers.CharField()
    vehicle_id = serializers.CharField()
    incident_type = serializers.CharField()
    severity = serializers.CharField()
    description = serializers.CharField()
    created_at = serializers.CharField()
    updated_at = serializers.CharField()


class IncidentQuerySerializer(serializers.Serializer):
    """Serializer for incident query filters."""

    incident_type = serializers.ChoiceField(
        choices=["HUMANO", "MECANICO"], required=False
    )
    severity = serializers.ChoiceField(choices=["LEVE", "GRAVE"], required=False)
    vehicle_id = serializers.CharField(max_length=20, required=False)
    driver_id = serializers.CharField(max_length=255, required=False)
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False)
