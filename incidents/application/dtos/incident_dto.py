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

    driver_id: str
    vehicle_id: str
    incident_type: str  # HUMANO or MECANICO
    severity: str  # LEVE or GRAVE
    description: str
    event_date: datetime


@dataclass
class IncidentResponseDTO:
    """
    Output DTO for incident responses.

    Represents the data returned to the client.
    """

    incident_id: str
    event_date: str
    driver_id: str
    vehicle_id: str
    incident_type: str
    severity: str
    description: Optional[str]
    created_at: str
    updated_at: str

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "incident_id": self.incident_id,
            "event_date": self.event_date,
            "driver_id": self.driver_id,
            "vehicle_id": self.vehicle_id,
            "incident_type": self.incident_type,
            "severity": self.severity,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
