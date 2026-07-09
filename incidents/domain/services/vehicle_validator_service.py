"""Vehicle Validator Service - Validates vehicle registration before incident creation."""

from incidents.domain.exceptions import (
    VehicleNotRegisteredException,
    VehicleServiceAuthenticationException,
    VehicleServiceUnavailableException,
)
from incidents.domain.ports import VehicleClientPort


class VehicleValidatorService:
    """
    Domain Service responsible for validating vehicle registration.

    Encapsulates the business rule: "An incident can only be registered
    for a vehicle that is registered in the system."

    Depends on VehicleClientPort (Hexagonal interface).
    """

    def __init__(self, vehicle_client: VehicleClientPort):
        """
        Initialize service with vehicle client adapter.

        Args:
            vehicle_client: Implementation of VehicleClientPort
        """
        self.vehicle_client = vehicle_client

    def validate_vehicle_exists(self, placa: str, authorization: str) -> None:
        """
        Validate that a vehicle plate is registered.

        Args:
            placa: Vehicle plate number
            authorization: Authorization header value

        Raises:
            VehicleNotRegisteredException: If plate is not registered
            VehicleServiceAuthenticationException: If auth fails validating vehicle
            VehicleServiceUnavailableException: If vehicle service unavailable
        """
        try:
            self.vehicle_client.validate_plate_exists(
                placa=placa, authorization=authorization
            )
        except (
            VehicleNotRegisteredException,
            VehicleServiceAuthenticationException,
            VehicleServiceUnavailableException,
        ):
            # Domain exceptions propagate as-is
            raise
        except Exception as e:
            # Unexpected errors from circuit breaker or network
            raise VehicleServiceUnavailableException(
                f"Failed to validate plate '{placa}': {str(e)}"
            )
