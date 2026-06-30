"""Unit tests for RabbitMQ producer adapter."""

import pytest

from incidents.infrastructure.adapters.messaging.rabbitmq_producer import (
    RabbitMQProducer,
)


class TestRabbitMQProducer:
    """Test RabbitMQ producer adapter."""

    @pytest.fixture
    def producer(self):
        """Create producer instance."""
        return RabbitMQProducer(
            rabbitmq_host="localhost",
            rabbitmq_port=5672,
        )

    def test_determine_routing_key_mecanico_grave(self, producer):
        """Given: Mechanical grave incident, When: Determine routing key, Then: Correct key."""
        event_data = {
            "incident_type": "MECANICO",
            "severity": "GRAVE",
        }

        key = producer._determine_routing_key(event_data)

        assert key == "incident.mecanico.grave"

    def test_determine_routing_key_mecanico_leve(self, producer):
        """Given: Mechanical mild incident, When: Determine key, Then: Correct key."""
        event_data = {
            "incident_type": "MECANICO",
            "severity": "LEVE",
        }

        key = producer._determine_routing_key(event_data)

        assert key == "incident.mecanico.leve"

    def test_determine_routing_key_humano(self, producer):
        """Given: Human incident, When: Determine key, Then: Humano key."""
        event_data = {
            "incident_type": "HUMANO",
            "severity": "GRAVE",
        }

        key = producer._determine_routing_key(event_data)

        assert key == "incident.humano"
