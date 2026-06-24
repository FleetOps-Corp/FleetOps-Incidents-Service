"""Incident domain events for event-driven workflow orchestration."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from typing import Optional


@dataclass
class IncidentRegisteredEvent:
    """
    Event published when an incident is successfully registered.
    
    Used by RabbitMQ consumers in Vehicles, Mantenimiento, and Asignaciones
    microservices to trigger their workflows.
    """

    incident_id: UUID
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
            "incident_id": str(self.incident_id),
            "id_conductor": self.id_conductor,
            "placa_vehiculo": self.placa_vehiculo,
            "tipo_incidente": self.tipo_incidente,
            "gravedad": self.gravedad,
            "descripcion": self.descripcion,
            "fecha_evento": self.fecha_evento.isoformat(),
        }

# dont think its so necessary given we do not use a confirmation nor state of incidente

# @dataclass
# class IncidentInGestionEvent:
    # """
    # Event published when an incident transitions to EN_GESTION state.
    
    # Indicates that all microservices have confirmed their actions
    # and the incident is now under management.
    # """

    # incident_id: UUID
    # estado_anterior: str
    # estado_nuevo: str
    # fecha_evento: datetime

    # def to_dict(self) -> dict:
        # """Convert event to dictionary for JSON serialization."""
        # return {
            # "event_type": "incident.in_gestion",
            # "incident_id": str(self.incident_id),
            # "estado_anterior": self.estado_anterior,
            # "estado_nuevo": self.estado_nuevo,
            # "fecha_evento": self.fecha_evento.isoformat(),
        # }
