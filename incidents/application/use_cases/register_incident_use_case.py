"""Register Incident Use Case - Primary workflow for incident registration."""

import logging

from incidents.application.dtos import IncidentDTO, IncidentResponseDTO
from incidents.application.exceptions import VehicleValidationError
from incidents.domain.exceptions import (
    DomainException,
    VehicleNotRegisteredException,
)
from incidents.domain.models import Incident
from incidents.domain.services import IncidentService, VehicleValidatorService


class RegisterIncidentUseCase:
    """
    Use Case: Register a new incident.

    Workflow (Workflow 1 from SAD):
    1. API Gateway receives request and authenticates user
    2. Validate vehicle plate exists (via VehicleClientPort)
    3. Create and persist incident
    4. Publish incident_registered event
    5. Return HTTP 201 with incident data

    SAGA coordination:
    - Vehicles marks vehicle unavailable (if grave)
    - Mantenimiento schedules maintenance (if grave + mecanico)
    - Asignaciones handles reassignment or delay notification

    This is the PRIMARY TRANSACTIONAL FLOW exercising all architectural layers.
    """

    def __init__(
        self,
        incident_service: IncidentService,
        vehicle_validator: VehicleValidatorService,
    ):
        """
        Initialize use case with domain services.

        Args:
            incident_service: Domain service for incident operations
            vehicle_validator: Domain service for vehicle validation
        """
        self.incident_service = incident_service
        self.vehicle_validator = vehicle_validator

    def execute(self, dto: IncidentDTO) -> IncidentResponseDTO:
        """
        Execute incident registration workflow.

        Args:
            dto: IncidentDTO with incident data from REST request

        Returns:
            IncidentResponseDTO with registered incident data

        Raises:
            VehicleValidationError: If plate is not registered
            DomainException: If incident data is invalid
        """
        # Step 1: Validate vehicle exists (Circuit Breaker protected)
        try:
            self.vehicle_validator.validate_vehicle_exists(dto.vehicle_id)
        except VehicleNotRegisteredException as e:
            raise VehicleValidationError(str(e))

        # Step 2: Register incident (domain logic, event publishing)
        try:
            incident = self.incident_service.register_incident(
                id_conductor=dto.driver_id,
                placa_vehiculo=dto.vehicle_id,
                tipo_incidente=dto.incident_type,
                gravedad=dto.severity,
                descripcion=dto.description,
                fecha_hora=dto.event_date,
            )
        except DomainException as e:
            logging.exception("A domain level error has happened")
            raise e

        # Step 3: Convert to response DTO
        return self._incident_to_response_dto(incident)

    @staticmethod
    def _incident_to_response_dto(incident: Incident) -> IncidentResponseDTO:
        """
        Convert domain Incident to response DTO.

        Args:
            incident: Domain incident model

        Returns:
            IncidentResponseDTO
        """
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
