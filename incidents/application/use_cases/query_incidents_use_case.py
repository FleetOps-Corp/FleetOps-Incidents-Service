"""Query Incidents Use Case - Retrieval and filtering of incidents."""

from typing import List

from incidents.application.dtos import IncidentResponseDTO, QueryFiltersDTO
from incidents.application.exceptions import IncidentNotFoundApplicationError
from incidents.domain.models import Incident
from incidents.domain.services import IncidentService


class QueryIncidentsUseCase:
    """
    Use Case: Query and filter incidents.

    Supports:
    - Filtering by type, severity, plate, conductor, date range
    - Combining multiple filters
    - Retrieving all incidents (no filter)

    (Workflow 3 from SAD - Consulta de Incidentes por el Servicio de Reportes)
    """

    def __init__(self, incident_service: IncidentService):
        """
        Initialize use case with domain service.

        Args:
            incident_service: Domain service for incident operations
        """
        self.incident_service = incident_service

    def execute(self, filters: QueryFiltersDTO) -> List[IncidentResponseDTO]:
        """
        Execute incident query with filters.

        Args:
            filters: QueryFiltersDTO with optional filter criteria

        Returns:
            List of IncidentResponseDTO matching filters
        """
        incidents = self.incident_service.query_incidents_by_filters(
            tipo_incidente=filters.incident_type,
            gravedad=filters.severity,
            placa=filters.vehicle_id,
            id_conductor=filters.driver_id,
            fecha_desde=filters.start_date,
            fecha_hasta=filters.end_date,
        )

        return [self._incident_to_response_dto(incident) for incident in incidents]

    def execute_by_id(self, incident_id: str) -> IncidentResponseDTO:
        incident = self.incident_service.find_by_id(
            incident_id
        )  # ← uses new service method
        if not incident:
            raise IncidentNotFoundApplicationError(
                f"Incident with ID {incident_id} not found."
            )
        return self._incident_to_response_dto(incident)

    @staticmethod
    def _incident_to_response_dto(incident: Incident) -> IncidentResponseDTO:
        """Convert domain Incident to response DTO."""
        return IncidentResponseDTO(
            incident_id=str(incident.id),
            event_date=incident.fecha_hora.isoformat(),
            driver_id=incident.id_conductor,
            vehicle_id=incident.get_plate_str(),
            incident_type=incident.tipo_incidente.value,
            severity=incident.gravedad.value,
            description=incident.descripcion,
            created_at=incident.created_at.isoformat(),
            updated_at=incident.updated_at.isoformat(),
        )
