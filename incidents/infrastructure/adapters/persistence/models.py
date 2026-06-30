"""Django ORM Models - Persistence layer mapping to PostgreSQL."""

from django.db import models


class Incident(models.Model):
    """
    Incident ORM Model - Maps to 'incidents' table in PostgreSQL.

    Immutable by design: Once created, core fields should not be modified.
    State transitions recorded in IncidentAudit table instead.
    """

    # Identity
    id = models.CharField(primary_key=True, max_length=20, editable=False)

    # Temporal
    fecha_hora = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Relationships
    id_conductor = models.CharField(max_length=255)  # FK to Conductores service
    placa_vehiculo = models.CharField(max_length=20)

    # Classification
    tipo_incidente = models.CharField(
        max_length=20,
        choices=[("HUMANO", "Human Incident"), ("MECANICO", "Mechanical Incident")],
    )
    gravedad = models.CharField(
        max_length=20, choices=[("LEVE", "Mild"), ("GRAVE", "Severe")]
    )

    # Content
    descripcion = models.TextField(null=False, blank=False)

    class Meta:
        db_table = "incidents"
        indexes = [
            models.Index(fields=["placa_vehiculo"]),
            models.Index(fields=["id_conductor"]),
            models.Index(fields=["tipo_incidente"]),
            models.Index(fields=["gravedad"]),
            models.Index(fields=["fecha_hora"]),
        ]

    def __str__(self):
        return f"Incident {self.id} - {self.tipo_incidente} ({self.gravedad})"
