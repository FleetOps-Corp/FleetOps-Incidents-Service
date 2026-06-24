"""Message Broker Port - Hexagonal interface for event publishing."""

from abc import ABC, abstractmethod
from typing import Dict, Any

# Revisar !!!

class MessageBrokerPort(ABC):
    """
    Hexagonal Port for asynchronous event publishing.
    
    Implementations will be in the infrastructure layer
    (e.g., RabbitMQ producer).
    """

    @abstractmethod
    def publish_incident_registered(self, event_data: Dict[str, Any]) -> None:
        """
        Publish an incident_registered event.
        
        Event routing:
        - Vehicles microservice: marks vehicle as unavailable (if grave)
        - Mantenimiento microservice: schedules maintenance (if grave + mecanico)
        - Asignaciones microservice: handles reassignment or delay notification
        
        Args:
            event_data: Event payload as dictionary
        """
        pass

    # @abstractmethod
    # def publish_incident_in_gestion(self, event_data: Dict[str, Any]) -> None:
    #     """
    #     Publish an incident_in_gestion event.
        
    #     Indicates incident is now under management after all SAGA confirmations.
        
    #     Args:
    #         event_data: Event payload as dictionary
    #     """
    #     pass

    @abstractmethod
    def publish_event(
        self, exchange_name: str, routing_key: str, event_data: Dict[str, Any]
    ) -> None:
        """
        Publish a generic event to a specific exchange.
        
        Low-level method for flexibility.
        
        Args:
            exchange_name: RabbitMQ exchange name
            routing_key: RabbitMQ routing key
            event_data: Event payload as dictionary
        """
        pass
