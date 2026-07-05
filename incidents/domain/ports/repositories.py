"""Repository Port - Hexagonal interface for incident persistence."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from incidents.domain.models import Incident


class IncidentRepository(ABC):
    """
    Hexagonal Port for incident persistence.

    Implementations will be in the infrastructure layer
    (e.g., Django ORM + PostgreSQL).
    """

    @abstractmethod
    def save(self, incident: Incident) -> Incident:
        """
        Persist an incident and return the saved instance.

        Args:
            incident: Incident aggregate to save

        Returns:
            Incident: The persisted incident (may have generated fields like ID)
        """
        pass

    @abstractmethod
    def find_by_id(self, incident_id: str) -> Optional[Incident]:
        """
        Retrieve an incident by its ID.

        Args:
            incident_id: The incident UUID

        Returns:
            Incident or None if not found
        """
        pass

    @abstractmethod
    def find_all(self) -> List[Incident]:
        """
        Retrieve all incidents.

        Returns:
            List of all incidents
        """
        pass

    @abstractmethod
    def find_by_placa(self, placa: str) -> List[Incident]:
        """
        Find all incidents for a given vehicle plate.

        Args:
            placa: Vehicle plate number

        Returns:
            List of incidents matching the plate
        """
        pass

    @abstractmethod
    def find_by_conductor(self, id_conductor: str) -> List[Incident]:
        """
        Find all incidents reported by a conductor.

        Args:
            id_conductor: Conductor identifier

        Returns:
            List of incidents for the conductor
        """
        pass

    @abstractmethod
    def find_by_date_range(
        self, fecha_desde: datetime, fecha_hasta: datetime
    ) -> List[Incident]:
        """
        Find incidents within a date range.

        Args:
            fecha_desde: Start date (inclusive)
            fecha_hasta: End date (inclusive)

        Returns:
            List of incidents in the date range
        """
        pass

    @abstractmethod
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
        Find incidents matching multiple filter criteria.

        Args:
            tipo_incidente: Filter by incident type (HUMANO or MECANICO)
            gravedad: Filter by severity (LEVE or GRAVE)
            placa: Filter by vehicle plate
            id_conductor: Filter by conductor ID
            fecha_desde: Filter by date range start
            fecha_hasta: Filter by date range end

        Returns:
            List of incidents matching all specified filters
        """
        pass
