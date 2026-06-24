"""HTTP Client Adapter - Calls Vehicles microservice with Circuit Breaker pattern."""

import requests
from pybreaker import CircuitBreaker
from typing import Optional, Dict, Any

from incidents.domain.ports import VehicleClientPort
from incidents.domain.exceptions import VehicleNotRegisteredException
from incidents.infrastructure.adapters.logging import logger_factory

logger = logger_factory.LoggerFactory().get_logger(__name__)


class VehicleClientWithCircuitBreaker(VehicleClientPort):
    """
    HTTP Client adapter for Vehicles microservice.
    
    Implements Circuit Breaker pattern to prevent cascading failures.
    This is the ONLY synchronous REST call allowed between microservices.
    
    Circuit Breaker states:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Threshold of failures exceeded, requests fail fast
    - HALF_OPEN: Testing if service recovered
    """

    def __init__(
        self,
        vehicles_api_url: str,
        timeout_seconds: float = 5.0,
        fail_max: int = 5,
        reset_timeout: int = 60,
    ):
        """
        Initialize client with Circuit Breaker.
        
        Args:
            vehicles_api_url: Base URL of Vehicles API (e.g., http://vehicles-service:8000)
            timeout_seconds: Request timeout
            fail_max: Number of failures before opening circuit
            reset_timeout: Seconds to wait before attempting half-open
        """
        self.vehicles_api_url = vehicles_api_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

        # Initialize Circuit Breaker
        self.breaker = CircuitBreaker(
            fail_max=fail_max,
            reset_timeout=reset_timeout,
            listeners=[self._breaker_listener()],
        )

    def validate_plate_exists(self, placa: str) -> bool:
        """
        Verify vehicle plate is registered (Circuit Breaker protected).
        
        Args:
            placa: Vehicle plate to validate
            
        Returns:
            bool: True if plate exists
            
        Raises:
            VehicleNotRegisteredException: If validation fails or service down
        """
        try:
            # Call through circuit breaker
            result = self.breaker.call(
                self._make_validation_request, placa
            )
            return result
        except Exception as e:
            logger.error(f"Vehicles API call failed for plate {placa}: {str(e)}")
            raise VehicleNotRegisteredException(
                f"Failed to validate plate {placa}: {str(e)}"
            )

    def get_vehicle_details(self, placa: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve vehicle details (optional).
        
        Args:
            placa: Vehicle plate
            
        Returns:
            Dictionary with vehicle details or None
        """
        try:
            url = f"{self.vehicles_api_url}/api/vehicles/{placa}"
            response = requests.get(url, timeout=self.timeout_seconds)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.warning(f"Failed to get vehicle details for {placa}: {str(e)}")
            return None

    def _make_validation_request(self, placa: str) -> bool:
        """
        Actual HTTP request to Vehicles API.
        
        Args:
            placa: Vehicle plate
            
        Returns:
            bool: True if plate exists
            
        Raises:
            Exception: On HTTP error
        """
        # Construct endpoint
        url = f"{self.vehicles_api_url}/api/vehicles/validate/{placa}"

        # Make request
        response = requests.get(url, timeout=self.timeout_seconds)

        # Handle responses
        if response.status_code == 200:
            # Plate is registered
            return True
        elif response.status_code == 404:
            # Plate not found
            return False
        else:
            # Other errors (500, etc.) should trigger circuit breaker
            response.raise_for_status()

    @staticmethod
    def _breaker_listener():
        """Create listener for circuit breaker state changes."""

        class CircuitBreakerListener:
            def state_change(self, breaker, before, after):
                logger.warning(
                    f"Circuit Breaker state change: {before} -> {after}"
                )

            def failure(self, breaker, exception):
                logger.warning(
                    f"Circuit Breaker recorded failure: {str(exception)}"
                )

            def success(self, breaker):
                logger.info("Circuit Breaker: Request succeeded")

        return CircuitBreakerListener()
