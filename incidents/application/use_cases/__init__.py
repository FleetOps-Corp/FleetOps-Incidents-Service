"""Use Cases - Application service layer orchestrating domain logic."""

from .query_incidents_use_case import QueryIncidentsUseCase
from .register_incident_use_case import RegisterIncidentUseCase

__all__ = [
    "RegisterIncidentUseCase",
    "QueryIncidentsUseCase",
]
