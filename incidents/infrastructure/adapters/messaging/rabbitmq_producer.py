"""RabbitMQ Message Broker Adapter - Producer for publishing events."""

# Revisar crear las colas y el enrutamiento correcto de los eventos a estas

import json
import pika
from typing import Dict, Any
from datetime import datetime

from incidents.domain.ports import MessageBrokerPort
from incidents.infrastructure.adapters.logging import logger_factory

logger = logger_factory.LoggerFactory().get_logger(__name__)


class RabbitMQProducer(MessageBrokerPort):
    """
    Message Broker adapter for publishing events to RabbitMQ.
    
    Publishes events for SAGA coordination:
    - incident.registered → Vehicles, Mantenimiento, Asignaciones
    - incident.in_gestion → Monitoring/reporting services
    
    Uses durable queues and exchanges for reliability.
    """

    def __init__(
        self,
        rabbitmq_host: str,
        rabbitmq_port: int = 5672,
        rabbitmq_user: str = "guest",
        rabbitmq_password: str = "guest",
        rabbitmq_vhost: str = "/",
    ):
        """
        Initialize RabbitMQ connection.
        
        Args:
            rabbitmq_host: RabbitMQ host
            rabbitmq_port: RabbitMQ port
            rabbitmq_user: Username
            rabbitmq_password: Password
            rabbitmq_vhost: Virtual host
        """
        self.rabbitmq_host = rabbitmq_host
        self.rabbitmq_port = rabbitmq_port
        self.rabbitmq_user = rabbitmq_user
        self.rabbitmq_password = rabbitmq_password
        self.rabbitmq_vhost = rabbitmq_vhost

        self.connection = None
        self.channel = None

    def _get_channel(self):
        """Get or create RabbitMQ channel."""
        if self.channel is None or self.channel.is_closed:
            credentials = pika.PlainCredentials(
                self.rabbitmq_user, self.rabbitmq_password
            )
            parameters = pika.ConnectionParameters(
                host=self.rabbitmq_host,
                port=self.rabbitmq_port,
                virtual_host=self.rabbitmq_vhost,
                credentials=credentials,
                connection_attempts=3,
                retry_delay=2,
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            self._declare_exchanges_and_queues()

        return self.channel

    def _declare_exchanges_and_queues(self):
        """Declare RabbitMQ topology (exchanges, queues, bindings)."""
        # Declare exchange
        self.channel.exchange_declare(
            exchange="incidents_events",
            exchange_type="topic",
            durable=True,
        )

        # Declare dead-letter exchange
        self.channel.exchange_declare(
            exchange="incidents_events_dlx",
            exchange_type="topic",
            durable=True,
        )

        logger.info("RabbitMQ topology declared")

    def publish_incident_registered(self, event_data: Dict[str, Any]) -> None:
        """
        Publish incident_registered event.
        
        Routing key determines which services receive the event based on incident type/severity.
        
        Args:
            event_data: Event dictionary with incident details
        """
        routing_key = self._determine_routing_key(event_data)
        self.publish_event(
            exchange_name="incidents_events",
            routing_key=routing_key,
            event_data=event_data,
        )
        logger.info(f"Published incident.registered event with routing key: {routing_key}")

    # def publish_incident_in_gestion(self, event_data: Dict[str, Any]) -> None:
    #     """
    #     Publish incident_in_gestion event.
        
    #     Args:
    #         event_data: Event dictionary
    #     """
    #     self.publish_event(
    #         exchange_name="incidents_events",
    #         routing_key="incident.in_gestion",
    #         event_data=event_data,
    #     )
    #     logger.info("Published incident.in_gestion event")

    def publish_event(
        self, exchange_name: str, routing_key: str, event_data: Dict[str, Any]
    ) -> None:
        """
        Publish generic event to RabbitMQ.
        
        Args:
            exchange_name: RabbitMQ exchange name
            routing_key: RabbitMQ routing key
            event_data: Event payload
        """
        try:
            channel = self._get_channel()

            # Serialize event
            message = json.dumps(event_data)

            # Publish with persistence
            channel.basic_publish(
                exchange=exchange_name,
                routing_key=routing_key,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=pika.DeliveryMode.Persistent,
                    content_type="application/json",
                ),
            )

            logger.debug(
                f"Event published to {exchange_name} with key {routing_key}"
            )
        except Exception as e:
            logger.error(f"Failed to publish event: {str(e)}")
            raise

    def close(self):
        """Close RabbitMQ connection."""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("RabbitMQ connection closed")

    @staticmethod
    def _determine_routing_key(event_data: Dict[str, Any]) -> str:
        """
        Determine routing key based on incident type and severity.
        
        Routing logic (from SAD):
        - mecanico.grave → Vehicles, Mantenimiento, Asignaciones
        - mecanico.leve → Asignaciones (delay notification)
        - humano.* → Asignaciones (conductor reassignment)
        
        Args:
            event_data: Event dictionary
            
        Returns:
            Routing key string
        """
        tipo = event_data.get("tipo_incidente", "").upper()
        gravedad = event_data.get("gravedad", "").upper()

        if tipo == "MECANICO":
            if gravedad == "GRAVE":
                return "incident.mecanico.grave"
            else:
                return "incident.mecanico.leve"
        elif tipo == "HUMANO":
            return "incident.humano"

        return "incident.unknown"
