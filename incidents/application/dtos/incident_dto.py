"""Incident DTOs - Transfer objects for incident data."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class IncidentDTO:
    """
    Input DTO for creating a new incident.
    
    Represents the data sent by a client in the REST API request.
    """

    id_conductor: str
    placa_vehiculo: str
    # Deberia ser valor numerico 1 o 2 ó los dejamos asi
    tipo_incidente: str  # HUMANO or MECANICO
    gravedad: str  # LEVE or GRAVE
    descripcion: str
    fecha_hora: datetime

@dataclass
class IncidentResponseDTO:
    """
    Output DTO for incident responses.
    
    Represents the data returned to the client.
    """
    
    id: str
    fecha_hora: str
    id_conductor: str
    placa_vehiculo: str
    tipo_incidente: str
    gravedad: str
    descripcion: Optional[str]
    created_at: str
    updated_at: str

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "fecha_hora": self.fecha_hora,
            "id_conductor": self.id_conductor,
            "placa_vehiculo": self.placa_vehiculo,
            "tipo_incidente": self.tipo_incidente,
            "gravedad": self.gravedad,
            "descripcion": self.descripcion,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
