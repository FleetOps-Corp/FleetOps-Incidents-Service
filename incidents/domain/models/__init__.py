"""Domain models - Aggregate roots and value objects."""

from .incident import Incident
from .value_objects import IncidentSeverity, IncidentType, PlateNumber

__all__ = [
    "Incident",
    "IncidentType",
    "IncidentSeverity",
    "PlateNumber",
]
