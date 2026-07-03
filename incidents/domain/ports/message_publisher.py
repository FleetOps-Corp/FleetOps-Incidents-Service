"""Message Publisher Port - Hexagonal interface for publishing domain events."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class MessagePublisherPort(ABC):
    """
    Hexagonal Port for publishing events to an external message queue.

    Implementations live in the infrastructure layer (e.g., AWS SQS adapter).
    This service ONLY publishes events; it does not consume messages.
    """

    @abstractmethod
    def publish(self, event_type: str, payload: Dict[str, Any]) -> None:
        """
        Publish an event to the queue.

        Args:
            event_type: Logical name of the event (e.g., "incident_registered")
            payload: Serializable event data

        Raises:
            Exception: If the message could not be sent
        """
        pass