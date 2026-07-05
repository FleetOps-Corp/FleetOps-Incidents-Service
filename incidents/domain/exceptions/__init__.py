"""Domain-specific exceptions."""

from .domain_exceptions import (
    DomainException,
    IncidentNotFoundError,
    InvalidIncidentSeverityException,
    InvalidIncidentTypeException,
    InvalidPlateNumberException,
    VehicleNotRegisteredException,
)

__all__ = [
    "DomainException",
    "InvalidIncidentTypeException",
    "InvalidIncidentSeverityException",
    "InvalidPlateNumberException",
    "VehicleNotRegisteredException",
    "IncidentNotFoundError",
]
