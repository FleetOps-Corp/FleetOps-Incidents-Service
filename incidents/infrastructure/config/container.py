import os

from django.conf import settings

from incidents.application.use_cases import (
    QueryIncidentsUseCase,
    RegisterIncidentUseCase,
)
from incidents.domain.ports import (
    MessagePublisherPort,
    VehicleClientPort,
)
from incidents.domain.services import IncidentService, VehicleValidatorService
from incidents.infrastructure.adapters.http_clients.vehicle_client_impl import (
    VehicleClientWithCircuitBreaker,
)
from incidents.infrastructure.adapters.messaging.sns_publisher import (
    SNSMessagePublisher,
)
from incidents.infrastructure.adapters.persistence.incident_repository import (
    DjangoIncidentRepository,
)
from incidents.infrastructure.api.views import set_use_cases


class DummyMessagePublisher(MessagePublisherPort):
    def publish(self, event_type: str, payload: dict) -> None:
        pass


class DummyVehicleClient(VehicleClientPort):
    def validate_plate_exists(self, placa: str) -> bool:
        return True

    def get_vehicle_details(self, placa: str):
        return None


def configure_application():
    repo = DjangoIncidentRepository()

    if settings.TESTING:
        vehicle_client = DummyVehicleClient()
        message_publisher = DummyMessagePublisher()
    else:
        vehicle_client = VehicleClientWithCircuitBreaker(
            vehicles_api_url=os.getenv("VEHICLES_API_URL"),
        )

        message_publisher = SNSMessagePublisher(
            topic_arn=os.getenv("SNS_TOPIC_ARN"),
            region_name=os.getenv("AWS_REGION"),
        )

    incident_service = IncidentService(repo, message_publisher)
    vehicle_validator = VehicleValidatorService(vehicle_client)

    set_use_cases(
        register_uc=RegisterIncidentUseCase(
            incident_service,
            vehicle_validator,
        ),
        query_uc=QueryIncidentsUseCase(incident_service),
    )