"""Incident Repository - Hexagonal Driven Adapter implementing IncidentRepository port."""

from typing import List, Optional
from datetime import datetime

from incidents.domain.models import Incident, IncidentType, IncidentSeverity, PlateNumber
from incidents.domain.ports import IncidentRepository
from incidents.infrastructure.adapters.persistence.models import (
    Incident as IncidentORM,
)


class DjangoIncidentRepository(IncidentRepository):
    """
    Repository implementation using Django ORM and PostgreSQL.
    
    Implements the IncidentRepository Hexagonal port.
    Isolated from domain layer via port abstraction.
    """

    def save(self, incident: Incident) -> Incident:
        """
        Persist an incident to PostgreSQL.
        
        Args:
            incident: Domain incident model
            
        Returns:
            Incident: The persisted incident (with ID if newly created)
        """
        assert incident.descripcion is not None
        
        orm_incident = IncidentORM(
            id=incident.id,
            fecha_hora=incident.fecha_hora,
            id_conductor=incident.id_conductor,
            placa_vehiculo=incident.get_plate_str(),
            tipo_incidente=incident.tipo_incidente.value,
            gravedad=incident.gravedad.value,
            descripcion=incident.descripcion,
        )
        orm_incident.save()
        return incident

    def find_by_id(self, incident_id: str) -> Optional[Incident]:
        """
        Retrieve incident by ID.
        
        Args:
            incident_id: UUID of incident
            
        Returns:
            Incident domain model or None
        """
        try:
            orm_incident = IncidentORM.objects.get(id=incident_id)
            return self._orm_to_domain(orm_incident)
        except IncidentORM.DoesNotExist:
            return None

    def find_all(self) -> List[Incident]:
        """
        Retrieve all incidents.
        
        Returns:
            List of incidents
        """
        orm_incidents = IncidentORM.objects.all()
        return [self._orm_to_domain(orm) for orm in orm_incidents]

    def find_by_placa(self, placa: str) -> List[Incident]:
        """
        Find incidents by vehicle plate.
        
        Args:
            placa: Vehicle plate number
            
        Returns:
            List of incidents for the plate
        """
        orm_incidents = IncidentORM.objects.filter(placa_vehiculo=placa)
        return [self._orm_to_domain(orm) for orm in orm_incidents]

    def find_by_conductor(self, id_conductor: str) -> List[Incident]:
        """
        Find incidents by conductor.
        
        Args:
            id_conductor: Conductor ID
            
        Returns:
            List of incidents for the conductor
        """
        orm_incidents = IncidentORM.objects.filter(id_conductor=id_conductor)
        return [self._orm_to_domain(orm) for orm in orm_incidents]

    def find_by_date_range(
        self, fecha_desde: datetime, fecha_hasta: datetime
    ) -> List[Incident]:
        """
        Find incidents within a date range.
        
        Args:
            fecha_desde: Start date
            fecha_hasta: End date
            
        Returns:
            List of incidents in range
        """
        orm_incidents = IncidentORM.objects.filter(
            fecha_hora__gte=fecha_desde, fecha_hora__lte=fecha_hasta
        )
        return [self._orm_to_domain(orm) for orm in orm_incidents]

    def find_by_filters(
        self,
        tipo_incidente: Optional[str] = None,
        gravedad: Optional[str] = None,
        placa: Optional[str] = None,
        id_conductor: Optional[str] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
    ) -> List[Incident]:
        """
        Find incidents matching multiple filters.
        
        Args:
            tipo_incidente: Filter by type (HUMANO or MECANICO)
            gravedad: Filter by severity (LEVE or GRAVE)
            placa: Filter by vehicle plate
            id_conductor: Filter by conductor ID
            fecha_desde: Date range start
            fecha_hasta: Date range end
            
        Returns:
            List of incidents matching all filters
        """
        query = IncidentORM.objects.all()

        if tipo_incidente:
            query = query.filter(tipo_incidente=tipo_incidente)
        if gravedad:
            query = query.filter(gravedad=gravedad)
        if placa:
            query = query.filter(placa_vehiculo=placa)
        if id_conductor:
            query = query.filter(id_conductor=id_conductor)
        if fecha_desde:
            query = query.filter(fecha_hora__gte=fecha_desde)
        if fecha_hasta:
            query = query.filter(fecha_hora__lte=fecha_hasta)

        return [self._orm_to_domain(orm) for orm in query]

    @staticmethod
    def _orm_to_domain(orm_incident: IncidentORM) -> Incident:
        """
        Convert Django ORM model to domain model.
        
        Args:
            orm_incident: ORM instance
            
        Returns:
            Incident: Domain model
        """
        return Incident(
            id=str(orm_incident.id),
            fecha_hora=orm_incident.fecha_hora,
            id_conductor=orm_incident.id_conductor,
            placa_vehiculo=PlateNumber(orm_incident.placa_vehiculo),
            tipo_incidente=IncidentType(orm_incident.tipo_incidente),
            gravedad=IncidentSeverity(orm_incident.gravedad),
            descripcion=orm_incident.descripcion,
            created_at=orm_incident.created_at,
            updated_at=orm_incident.updated_at,
        )
