"""Django app configuration."""

import os

from django.apps import AppConfig
from dotenv import load_dotenv

load_dotenv()


class IncidentsConfig(AppConfig):
    """Configuration for Incidents microservice Django app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "incidents"
    verbose_name = "Incidents Microservice - FleetOps Platform"

    def ready(self):
        """Wire up use case dependencies on app startup."""
        from incidents.application.use_cases import (
            QueryIncidentsUseCase,
            RegisterIncidentUseCase,
        )
        from incidents.domain.ports import VehicleClientPort
        from incidents.domain.services import IncidentService, VehicleValidatorService
        from incidents.infrastructure.adapters.messaging.sqs_publisher import (
            SQSMessagePublisher,
        )
        from incidents.infrastructure.adapters.persistence.incident_repository import (
            DjangoIncidentRepository,
        )
        from incidents.infrastructure.api.views import set_use_cases

        # from incidents.infrastructure.adapters.http_clients.vehicle_client_impl import VehicleClientWithCircuitBreaker

        class DummyVehicleClient(VehicleClientPort):
            def validate_plate_exists(self, placa: str) -> bool:
                return True  # siempre válido

            def get_vehicle_details(self, placa: str):
                return None

        # Layer 1: Driven adapters
        repo = DjangoIncidentRepository()

        # vehicle_client = VehicleClientWithCircuitBreaker(
        #     vehicles_api_url=os.getenv("VEHICLES_API_URL"),
        # )

        vehicle_client = DummyVehicleClient()

        message_publisher = SQSMessagePublisher(
            queue_url=os.getenv("SQS_QUEUE_URL"),
            region_name=os.getenv("AWS_REGION"),
        )

        # Layer 2: Domain services
        incident_service = IncidentService(repo, message_publisher)
        vehicle_validator = VehicleValidatorService(vehicle_client)

        # Layer 3: Use cases
        set_use_cases(
            register_uc=RegisterIncidentUseCase(incident_service, vehicle_validator),
            query_uc=QueryIncidentsUseCase(incident_service),
        )
