"""Incident domain events for event-driven workflow orchestration."""

from dataclasses import dataclass
from datetime import datetime

@dataclass
class IncidentRegisteredEvent:
    """
    Event published when an incident is successfully registered.
    
    Used by RabbitMQ consumers in Vehicles, Mantenimiento, and Asignaciones
    microservices to trigger their workflows.
    """

    incident_id: str
    id_conductor: str
    placa_vehiculo: str
    tipo_incidente: str  # HUMANO or MECANICO
    gravedad: str  # LEVE or GRAVE
    descripcion: str
    fecha_evento: datetime

    def to_dict(self) -> dict:
        """Convert event to dictionary for JSON serialization."""
        return {
            "event_type": "incident.registered",
            "incident_id": self.incident_id,
            "driver_id": self.id_conductor,
            "vehicle_id": self.placa_vehiculo,
            "incident_type": self.tipo_incidente,
            "severity": self.gravedad,
            "description": self.descripcion,
            "event_date": self.fecha_evento.isoformat(),
        }