"""Query Incidents Use Case - Retrieval and filtering of incidents."""

from typing import List
from datetime import datetime
from uuid import UUID

from incidents.domain.services import IncidentService
from incidents.domain.models import Incident
from incidents.application.dtos import IncidentResponseDTO, QueryFiltersDTO
from incidents.application.exceptions import IncidentNotFoundApplicationError


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
            tipo_incidente=filters.tipo_incidente,
            gravedad=filters.gravedad,
            placa=filters.placa,
            id_conductor=filters.id_conductor,
            fecha_desde=filters.fecha_desde,
            fecha_hasta=filters.fecha_hasta,
        )

        return [
            self._incident_to_response_dto(incident)
            for incident in incidents
        ]

    def execute_by_id(self, incident_id: str) -> IncidentResponseDTO:
        incident = self.incident_service.find_by_id(incident_id)  # ← uses new service method
        if not incident:
            raise IncidentNotFoundApplicationError(
                f"Incident with ID {incident_id} not found."
            )
        return self._incident_to_response_dto(incident)

    @staticmethod
    def _incident_to_response_dto(incident: Incident) -> IncidentResponseDTO:
        """Convert domain Incident to response DTO."""
        return IncidentResponseDTO(
            id=str(incident.id),
            fecha_hora=incident.fecha_hora.isoformat(),
            id_conductor=incident.id_conductor,
            placa_vehiculo=incident.get_plate_str(),
            tipo_incidente=incident.tipo_incidente.value,
            gravedad=incident.gravedad.value,
            descripcion=incident.descripcion,
            # estado=incident.estado, # delete this
            created_at=incident.created_at.isoformat(),
            updated_at=incident.updated_at.isoformat(),
        )
