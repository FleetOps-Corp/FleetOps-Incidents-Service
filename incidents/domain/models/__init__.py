"""Domain models - Aggregate roots and value objects."""

from .incident import Incident
from .value_objects import IncidentType, IncidentSeverity, PlateNumber

__all__ = [
    "Incident",
    "IncidentType",
    "IncidentSeverity",
    "PlateNumber",
]
