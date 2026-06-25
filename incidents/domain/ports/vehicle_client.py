"""Vehicle Client Port - Hexagonal interface for Vehicles microservice interaction."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class VehicleClientPort(ABC):
    """
    Hexagonal Port for synchronous communication with Vehicles microservice.

    This is the ONLY synchronous (REST) call allowed between microservices.
    It is protected by Circuit Breaker pattern.

    Implementations will be in the infrastructure layer
    (e.g., HTTP client with pybreaker).
    """

    @abstractmethod
    def validate_plate_exists(self, placa: str) -> bool:
        """
        Verify that a vehicle plate is registered in the system.

        CRITICAL: This call MUST be protected by Circuit Breaker.
        If the Vehicles service is down, this should fail fast
        and return False or raise an exception, not hang.

        Args:
            placa: Vehicle plate number to validate

        Returns:
            bool: True if plate is registered, False otherwise

        Raises:
            VehicleNotRegisteredException: If validation fails
        """
        pass

    @abstractmethod
    def get_vehicle_details(self, placa: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve vehicle details (optional extended method).

        Args:
            placa: Vehicle plate number

        Returns:
            Dictionary with vehicle details or None if not found
        """
        pass
