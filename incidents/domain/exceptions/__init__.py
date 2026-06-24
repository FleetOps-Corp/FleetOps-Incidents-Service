"""Domain-specific exceptions."""
from .domain_exceptions import (
    DomainException,
    InvalidIncidentTypeException,
    InvalidIncidentSeverityException,
    InvalidPlateNumberException,
    VehicleNotRegisteredException,
    IncidentNotFoundError,
)

__all__ = [
    "DomainException",
    "InvalidIncidentTypeException",
    "InvalidIncidentSeverityException",
    "InvalidPlateNumberException",
    "VehicleNotRegisteredException",
    "IncidentNotFoundError",
]
