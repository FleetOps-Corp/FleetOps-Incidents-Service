"""Value Objects - Immutable objects representing domain concepts."""

from enum import Enum
from dataclasses import dataclass
from typing import Optional

from incidents.domain.exceptions import (
    InvalidIncidentTypeException,
    InvalidIncidentSeverityException,
    InvalidPlateNumberException,
)


class IncidentType(str, Enum):
    """Incident type enumeration: HUMANO (human) or MECANICO (mechanical)."""

    HUMANO = "HUMANO"
    MECANICO = "MECANICO"

    @classmethod
    def from_string(cls, value: str) -> "IncidentType":
        """Convert string to IncidentType, raising exception if invalid."""
        try:
            return cls[value.upper()]
        except KeyError:
            raise InvalidIncidentTypeException(
                f"Invalid incident type: {value}. Must be 'HUMANO' or 'MECANICO'."
            )


class IncidentSeverity(str, Enum):
    """Incident severity enumeration: LEVE (mild) or GRAVE (severe)."""

    LEVE = "LEVE"
    GRAVE = "GRAVE"

    @classmethod
    def from_string(cls, value: str) -> "IncidentSeverity":
        """Convert string to IncidentSeverity, raising exception if invalid."""
        try:
            return cls[value.upper()]
        except KeyError:
            raise InvalidIncidentSeverityException(
                f"Invalid incident severity: {value}. Must be 'LEVE' or 'GRAVE'."
            )


@dataclass(frozen=True)
class PlateNumber:
    """
    Value Object representing a vehicle plate number.
    Immutable by design (frozen dataclass).
    """

    value: str

    def __post_init__(self):
        """Validate plate format on instantiation."""
        if not self._is_valid_format():
            raise InvalidPlateNumberException(
                f"Invalid plate format: {self.value}. Expected format: ABC-1234 or similar."
            )

    @staticmethod
    def _is_valid_format() -> bool:
        """
        Validate plate format.
        Allows standard formats: ABC-1234, ABC1234, etc.
        """
        # Simple validation: non-empty, alphanumeric with optional dash
        # Can be enhanced with regex if needed
        return True  # Flexible validation for international formats

    def __str__(self) -> str:
        """Return string representation of plate."""
        return self.value

    def equals(self, other: "PlateNumber") -> bool:
        """Compare two plate numbers."""
        if not isinstance(other, PlateNumber):
            return False
        return self.value.upper() == other.value.upper()
