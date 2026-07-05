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

    incident_type: Optional[str] = None
    severity: Optional[str] = None
    vehicle_id: Optional[str] = None
    driver_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in self.__dict__.items() if v is not None}
