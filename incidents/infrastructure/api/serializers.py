"""REST API Serializers - Conversion between JSON and domain models."""

from rest_framework import serializers
from datetime import datetime
from typing import Optional


class IncidentRequestSerializer(serializers.Serializer):
    """Deserializer for incident creation requests."""

    id_conductor = serializers.CharField(max_length=255, required=True, allow_blank=False)
    placa_vehiculo = serializers.CharField(max_length=20)
    tipo_incidente = serializers.ChoiceField(choices=["HUMANO", "MECANICO"])
    gravedad = serializers.ChoiceField(choices=["LEVE", "GRAVE"])
    descripcion = serializers.CharField(required=True, allow_blank=False)
    fecha_hora = serializers.DateTimeField(required=True)

    def validate_id_conductor(self, value):
        """Validate conductor ID format."""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Conductor ID cannot be empty")
        return value

    def validate_placa_vehiculo(self, value):
        """Validate plate format."""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Plate number cannot be empty")
        return value.upper().strip()


class IncidentResponseSerializer(serializers.Serializer):
    """Serializer for incident responses."""

    id = serializers.CharField()
    fecha_hora = serializers.CharField()
    id_conductor = serializers.CharField()
    placa_vehiculo = serializers.CharField()
    tipo_incidente = serializers.CharField()
    gravedad = serializers.CharField()
    descripcion = serializers.CharField()
    created_at = serializers.CharField()
    updated_at = serializers.CharField()


class IncidentQuerySerializer(serializers.Serializer):
    """Serializer for incident query filters."""

    tipo_incidente = serializers.ChoiceField(
        choices=["HUMANO", "MECANICO"], required=False
    )
    gravedad = serializers.ChoiceField(
        choices=["LEVE", "GRAVE"], required=False
    )
    placa = serializers.CharField(max_length=20, required=False)
    id_conductor = serializers.CharField(max_length=255, required=False)
    fecha_desde = serializers.DateTimeField(required=False)
    fecha_hasta = serializers.DateTimeField(required=False)
