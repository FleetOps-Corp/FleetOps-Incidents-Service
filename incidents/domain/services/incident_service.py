"""Incident Domain Service - Core business logic orchestration."""

import logging
from datetime import datetime
from typing import List, Optional

from incidents.domain.models import Incident
from incidents.domain.ports import IncidentRepository, MessagePublisherPort


class IncidentService:
    """
    Domain Service for incident management.

    Orchestrates:
    - Incident creation and validation
    - Event publishing to trigger SAGA workflows
    - Incident querying with filters
    """

    def __init__(self, incident_repo: IncidentRepository, message_publisher: MessagePublisherPort):
        """
        Initialize service with repository and message publisher adapters.

        Args:
            incident_repo: Implementation of IncidentRepository
            message_publisher: Implementation of MessagePublisherPort
        """
        self.incident_repo = incident_repo
        self.message_publisher = message_publisher

    def register_incident(
        self,
        id_conductor: str,
        placa_vehiculo: str,
        tipo_incidente: str,
        gravedad: str,
        descripcion: str,
        fecha_hora: datetime,
    ) -> Incident:
        """
        Register a new incident (Core Business Process).

        Workflow:
        1. Create incident aggregate (validates all inputs)
        2. Persist to repository
        3. Publish incident_registered event for SAGA coordination

        Args:
            id_conductor: Conductor identifier
            placa_vehiculo: Vehicle plate (assumed validated externally)
            tipo_incidente: Type (HUMANO or MECANICO)
            gravedad: Severity (LEVE or GRAVE)
            descripcion:  detailed description
            fecha_hora:  timestamp (defaults to now)

        Returns:
            Incident: The registered incident

        Raises:
            InvalidIncidentTypeException: If tipo_incidente is invalid
            InvalidIncidentSeverityException: If gravedad is invalid
            InvalidPlateNumberException: If placa_vehiculo format is invalid
        """
        # Create incident aggregate (factory validates inputs)
        incident = Incident.create(
            id_conductor=id_conductor,
            placa_vehiculo=placa_vehiculo,
            tipo_incidente=tipo_incidente,
            gravedad=gravedad,
            descripcion=descripcion,
            fecha_hora=fecha_hora,
        )

        # Persist
        saved_incident = self.incident_repo.save(incident)

        # Publish event for SAGA coordination.
        # Business decision: a publishing failure must NOT block the
        # transactional flow. The incident is already persisted and the
        # API must still return 201.
        self._publish_incident_registered_event(saved_incident)

        return saved_incident

    def query_incidents_by_filters(
        self,
        tipo_incidente: Optional[str] = None,
        gravedad: Optional[str] = None,
        placa: Optional[str] = None,
        id_conductor: Optional[str] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
    ) -> List[Incident]:
        """
        Query incidents with optional filters.

        Args:
            tipo_incidente: Filter by type (HUMANO or MECANICO)
            gravedad: Filter by severity (LEVE or GRAVE)
            placa: Filter by vehicle plate
            id_conductor: Filter by conductor ID
            fecha_desde: Filter by date range start
            fecha_hasta: Filter by date range end

        Returns:
            List of incidents matching criteria
        """
        return self.incident_repo.find_by_filters(
            tipo_incidente=tipo_incidente,
            gravedad=gravedad,
            placa=placa,
            id_conductor=id_conductor,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
        )

    def _publish_incident_registered_event(self, incident: Incident) -> None:
        """
        Publish incident_registered event for SAGA orchestration.

        This event is consumed by:
        - Vehicles: marks vehicle unavailable (if grave)
        - Mantenimiento: schedules maintenance (if grave + mecanico)
        - Asignaciones: handles reassignment or delay notification

        Failures are logged but NOT re-raised: publishing is best-effort
        and must not affect the transactional response to the client.

        Args:
            incident: The incident to publish
        """
        try:
            self.message_publisher.publish(
                event_type="incident_registered",
                payload=incident.to_dict(),
            )
        except Exception as e:
            logging.exception(
                f"Failed to publish incident_registered event for {incident.id}: {str(e)}"
            )

    def find_by_id(self, incident_id: str) -> Optional[Incident]:
        """Retrieve a single incident by ID."""
        return self.incident_repo.find_by_id(incident_id)