"""Query Filters DTO - Transfer object for incident query parameters."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class QueryFiltersDTO:
    """
    DTO for incident query parameters.

    Encapsulates all possible filters for incident searches.
    """

    tipo_incidente: Optional[str] = None
    gravedad: Optional[str] = None
    placa: Optional[str] = None
    id_conductor: Optional[str] = None
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in self.__dict__.items() if v is not None}
