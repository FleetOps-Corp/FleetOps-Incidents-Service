"""Incident Aggregate Root - Core domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from incidents.domain.models.value_objects import (
    IncidentType,
    IncidentSeverity,
    PlateNumber,
)


@dataclass
class Incident:
    """
    Incident Aggregate Root (DDD).
    Represents a vehicle or driver incident report.
    Core fields are immutable after creation.

    ID format: INC-{TIPO}-{GRAVEDAD}-{YYYYMMDD}-{SHORT_UUID}
    Example:   INC-HUM-LEV-20260621-a3f9
    """

    # Relationships
    id_conductor: str
    placa_vehiculo: PlateNumber

    # Temporal
    fecha_hora: datetime

    # Classification
    tipo_incidente: IncidentType
    gravedad: IncidentSeverity

    # Content
    descripcion: str

    # Identity (generated, so goes after required fields)
    id: str = field(default="")  # ← changed: now str, generated in create()

    # Audit
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def _generate_id(
        cls,
        tipo_incidente: IncidentType,
        gravedad: IncidentSeverity,
        fecha_hora: datetime,
    ) -> str:
        """
        Generate human-readable incident ID.

        Format: INC-{YYYYMMDD}-{SHORT_UUID}
        Example: INC-20260621-a3f9

        Args:
            tipo_incidente: Incident type enum
            gravedad: Severity enum
            fecha_hora: Incident timestamp

        Returns:
            str: Generated incident ID
        """
        date_code = fecha_hora.strftime("%Y%m%d")
        short_uuid = str(uuid4())[:4]  # e.g. "a3f9"
        return f"INC-{date_code}-{short_uuid}"

    @classmethod
    def create(
        cls,
        id_conductor: str,
        placa_vehiculo: str,
        tipo_incidente: str,
        gravedad: str,
        descripcion: str,
        fecha_hora: datetime,
    ) -> "Incident":
        """
        Factory method to create a new Incident.

        Validates all inputs and converts to appropriate value objects.
        Generates a human-readable ID combining type, severity, date, and UUID.

        Args:
            id_conductor: Conductor identifier
            placa_vehiculo: Vehicle plate number
            tipo_incidente: Type of incident (HUMANO or MECANICO)
            gravedad: Severity level (LEVE or GRAVE)
            descripcion: Optional description
            fecha_hora: Optional timestamp (defaults to now)

        Returns:
            Incident: New incident instance

        Raises:
            InvalidIncidentTypeException: If tipo_incidente is invalid
            InvalidIncidentSeverityException: If gravedad is invalid
            InvalidPlateNumberException: If placa_vehiculo format is invalid
        """
        tipo = IncidentType.from_string(tipo_incidente)
        sev = IncidentSeverity.from_string(gravedad)
        placa = PlateNumber(placa_vehiculo)
        fecha = fecha_hora or datetime.utcnow()  # ← default to now if not provided
        incident_id = cls._generate_id(tipo, sev, fecha)

        return cls(
            id=incident_id,
            id_conductor=id_conductor,
            placa_vehiculo=placa,
            tipo_incidente=tipo,
            gravedad=sev,
            descripcion=descripcion,
            fecha_hora=fecha,
        )

    def get_plate_str(self) -> str:
        """Return plate as string for external communication."""
        return str(self.placa_vehiculo)

    def is_grave(self) -> bool:
        return self.gravedad == IncidentSeverity.GRAVE

    def is_leve(self) -> bool:
        return self.gravedad == IncidentSeverity.LEVE

    def is_humano(self) -> bool:
        return self.tipo_incidente == IncidentType.HUMANO

    def is_mecanico(self) -> bool:
        return self.tipo_incidente == IncidentType.MECANICO

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "fecha_hora": self.fecha_hora.isoformat(),
            "id_conductor": self.id_conductor,
            "placa_vehiculo": self.get_plate_str(),
            "tipo_incidente": self.tipo_incidente.value,
            "gravedad": self.gravedad.value,
            "descripcion": self.descripcion,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
