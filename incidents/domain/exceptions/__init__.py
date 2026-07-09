"""Domain-specific exceptions."""

from .domain_exceptions import (
    DomainException,
    IncidentNotFoundError,
    InvalidIncidentSeverityException,
    InvalidIncidentTypeException,
    InvalidPlateNumberException,
    VehicleNotRegisteredException,
    VehicleServiceAuthenticationException,
    VehicleServiceUnavailableException,
)

__all__ = [
    "DomainException",
    "InvalidIncidentTypeException",
    "InvalidIncidentSeverityException",
    "InvalidPlateNumberException",
    "VehicleNotRegisteredException",
    "VehicleServiceAuthenticationException",
    "VehicleServiceUnavailableException",
    "IncidentNotFoundError",
]
