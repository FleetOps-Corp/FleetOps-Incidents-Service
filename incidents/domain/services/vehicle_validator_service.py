"""Vehicle Validator Service - Validates vehicle registration before incident creation."""

from incidents.domain.exceptions import VehicleNotRegisteredException
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

        Raises:
            VehicleNotRegisteredException: If plate is not registered or validation fails
        """
        try:
            is_valid = self.vehicle_client.validate_plate_exists(placa=placa, authorization=authorization)
            if not is_valid:
                raise VehicleNotRegisteredException(
                    f"Plate '{placa}' is not registered in the system."
                )
        except Exception as e:
            # Circuit breaker or network error
            if isinstance(e, VehicleNotRegisteredException):
                raise
            raise VehicleNotRegisteredException(
                f"Failed to validate plate '{placa}': {str(e)}"
            )
