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
        config_module = importlib.import_module(
            "incidents.infrastructure.config.django_setup"
        )

        container_module = importlib.import_module(
            "incidents.infrastructure.config.container"
        )

        configure_mock = Mock()

        monkeypatch.setattr(
            container_module,
            "configure_application",
            configure_mock,
        )

        config = config_module.IncidentsConfig("incidents", incidents)
        config.ready()

        configure_mock.assert_called_once()
