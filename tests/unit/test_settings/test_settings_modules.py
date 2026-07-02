"""Unit tests for Django settings and app configuration modules."""

import importlib
from unittest.mock import Mock

import incidents


class TestSettingsModules:
    def test_base_settings_use_environment_values(self, monkeypatch):
        monkeypatch.setenv("DJANGO_SECRET_KEY", "secret-value")
        monkeypatch.setenv("DB_NAME", "fleetops")
        monkeypatch.setenv("DB_USER", "fleetops_user")
        monkeypatch.setenv("DB_PASSWORD", "fleetops_pass")
        monkeypatch.setenv("DB_HOST", "db.local")
        monkeypatch.setenv("DB_PORT", "5432")

        base = importlib.import_module("incidents.settings.base")
        importlib.reload(base)

        assert base.SECRET_KEY == "secret-value"
        assert base.DATABASES["default"]["NAME"] == "fleetops"
        assert base.INSTALLED_APPS[-1].endswith("IncidentsConfig")

    def test_development_settings_override_database_host_and_port(self, monkeypatch):
        monkeypatch.setenv("DB_HOST", "dev-db.local")
        monkeypatch.setenv("DB_PORT", "15432")

        base = importlib.import_module("incidents.settings.base")
        importlib.reload(base)
        development = importlib.import_module("incidents.settings.development")
        importlib.reload(development)

        assert development.DEBUG is False
        assert development.DATABASES["default"]["HOST"] == "dev-db.local"
        assert development.DATABASES["default"]["PORT"] == "15432"

    def test_production_settings_enable_security_flags(self, monkeypatch):
        monkeypatch.setenv("DJANGO_ALLOWED_HOSTS", "app.local,api.local")
        monkeypatch.setenv(
            "CORS_ALLOWED_ORIGINS", "https://app.local,https://admin.local"
        )

        base = importlib.import_module("incidents.settings.base")
        importlib.reload(base)
        production = importlib.import_module("incidents.settings.production")
        importlib.reload(production)

        assert production.DEBUG is False
        assert production.ALLOWED_HOSTS == ["app.local", "api.local"]
        assert production.SECURE_SSL_REDIRECT is True
        assert production.CORS_ALLOWED_ORIGINS == [
            "https://app.local",
            "https://admin.local",
        ]

    def test_app_config_ready_wires_use_cases(self, monkeypatch):
        views_module = importlib.import_module("incidents.infrastructure.api.views")
        repo_module = importlib.import_module(
            "incidents.infrastructure.adapters.persistence.incident_repository"
        )
        use_cases_module = importlib.import_module("incidents.application.use_cases")
        services_module = importlib.import_module("incidents.domain.services")

        set_use_cases = Mock()
        repo = Mock(name="repo")
        incident_service = Mock(name="incident_service")
        vehicle_validator = Mock(name="vehicle_validator")
        register_uc = Mock(name="register_uc")
        query_uc = Mock(name="query_uc")

        monkeypatch.setattr(views_module, "set_use_cases", set_use_cases)
        monkeypatch.setattr(
            repo_module, "DjangoIncidentRepository", Mock(return_value=repo)
        )
        monkeypatch.setattr(
            services_module, "IncidentService", Mock(return_value=incident_service)
        )
        monkeypatch.setattr(
            services_module,
            "VehicleValidatorService",
            Mock(return_value=vehicle_validator),
        )
        monkeypatch.setattr(
            use_cases_module,
            "RegisterIncidentUseCase",
            Mock(return_value=register_uc),
        )
        monkeypatch.setattr(
            use_cases_module,
            "QueryIncidentsUseCase",
            Mock(return_value=query_uc),
        )

        config_module = importlib.import_module(
            "incidents.infrastructure.config.django_setup"
        )
        importlib.reload(config_module)
        config = config_module.IncidentsConfig("incidents", incidents)

        config.ready()

        set_use_cases.assert_called_once_with(
            register_uc=register_uc,
            query_uc=query_uc,
        )
