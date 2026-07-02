"""Hexagonal Ports - Interfaces for adapters (both incoming and outgoing)."""

from .repositories import IncidentRepository
from .vehicle_client import VehicleClientPort

__all__ = [
    "IncidentRepository",
    "VehicleClientPort",
]
