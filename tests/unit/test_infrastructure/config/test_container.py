from unittest.mock import Mock

from incidents.infrastructure.config import container


class TestConfigureApp:

    def test_configure_application_testing(self, monkeypatch):
        """Should wire dummy implementations when TESTING=True."""

        monkeypatch.setattr(container.settings, "TESTING", True)

        repo = Mock()
        incident_service = Mock()
        validator = Mock()
        register_uc = Mock()
        query_uc = Mock()
        set_use_cases = Mock()

        monkeypatch.setattr(
            container,
            "DjangoIncidentRepository",
            Mock(return_value=repo),
        )

        monkeypatch.setattr(
            container,
            "IncidentService",
            Mock(return_value=incident_service),
        )

        monkeypatch.setattr(
            container,
            "VehicleValidatorService",
            Mock(return_value=validator),
        )

        monkeypatch.setattr(
            container,
            "RegisterIncidentUseCase",
            Mock(return_value=register_uc),
        )

        monkeypatch.setattr(
            container,
            "QueryIncidentsUseCase",
            Mock(return_value=query_uc),
        )

        monkeypatch.setattr(
            container,
            "set_use_cases",
            set_use_cases,
        )

        container.configure_application()

        container.IncidentService.assert_called_once()
        container.VehicleValidatorService.assert_called_once()

        # Dummy vehicle client and SNS publisher should have been used
        vehicle_client = container.VehicleValidatorService.call_args[0][0]
        message_publisher = container.IncidentService.call_args[0][1]

        assert isinstance(vehicle_client, container.DummyVehicleClient)
        assert isinstance(message_publisher, container.SNSMessagePublisher)

        set_use_cases.assert_called_once_with(
            register_uc=register_uc,
            query_uc=query_uc,
        )

    def test_configure_application_production(self, monkeypatch):
        """Should wire real adapters when TESTING=False."""

        monkeypatch.setattr(container.settings, "TESTING", False)

        monkeypatch.setenv("VEHICLES_API_URL", "http://vehicles")
        monkeypatch.setenv("AWS_REGION", "us-east-1")
        monkeypatch.setenv("SNS_TOPIC_ARN", "https://queue")

        repo = Mock()
        vehicle_client = Mock()
        publisher = Mock()
        incident_service = Mock()
        validator = Mock()
        register_uc = Mock()
        query_uc = Mock()
        set_use_cases = Mock()

        monkeypatch.setattr(
            container,
            "DjangoIncidentRepository",
            Mock(return_value=repo),
        )

        monkeypatch.setattr(
            container,
            "VehicleClientWithCircuitBreaker",
            Mock(return_value=vehicle_client),
        )

        monkeypatch.setattr(
            container,
            "SNSMessagePublisher",
            Mock(return_value=publisher),
        )

        monkeypatch.setattr(
            container,
            "IncidentService",
            Mock(return_value=incident_service),
        )

        monkeypatch.setattr(
            container,
            "VehicleValidatorService",
            Mock(return_value=validator),
        )

        monkeypatch.setattr(
            container,
            "RegisterIncidentUseCase",
            Mock(return_value=register_uc),
        )

        monkeypatch.setattr(
            container,
            "QueryIncidentsUseCase",
            Mock(return_value=query_uc),
        )

        monkeypatch.setattr(
            container,
            "set_use_cases",
            set_use_cases,
        )

        container.configure_application()

        container.VehicleClientWithCircuitBreaker.assert_called_once_with(
            vehicles_api_url="http://vehicles",
        )

        container.SNSMessagePublisher.assert_called_once_with(
            topic_arn="https://queue",
            region_name="us-east-1",
        )

        set_use_cases.assert_called_once_with(
            register_uc=register_uc,
            query_uc=query_uc,
        )
