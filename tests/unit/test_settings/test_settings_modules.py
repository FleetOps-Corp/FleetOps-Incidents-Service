"""Unit tests for Django settings and app configuration modules."""

import importlib
import json
import sys
from unittest.mock import Mock

from django.test import RequestFactory

import incidents
import incidents.urls as incidents_urls
from incidents.urls import health_check


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
        assert base.INSTALLED_APPS[-1].endswith("django_prometheus")

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

    def test_health_check_returns_ok_payload(self):
        request = RequestFactory().get("/health")

        response = health_check(request)

        assert response.status_code == 200
        assert json.loads(response.content) == {
            "status": "ok",
            "service": "incidents",
        }

    def test_health_check_rejects_post_requests(self):
        request = RequestFactory().post("/health")

        response = health_check(request)

        assert response.status_code == 405

    def test_health_urlpattern_is_registered(self):
        health_pattern = incidents_urls.urlpatterns[0]

        assert str(health_pattern.pattern) == "health"
        assert health_pattern.name == "health_check"

    def test_wsgi_module_sets_default_settings_and_exposes_application(
        self, monkeypatch
    ):
        monkeypatch.delenv("DJANGO_SETTINGS_MODULE", raising=False)

        stub_application = object()

        monkeypatch.setattr(
            "django.core.wsgi.get_wsgi_application",
            lambda: stub_application,
        )

        sys.modules.pop("incidents.wsgi", None)
        wsgi_module = importlib.import_module("incidents.wsgi")

        assert wsgi_module.application is stub_application
        assert (
            importlib.import_module("os").environ["DJANGO_SETTINGS_MODULE"]
            == "incidents.settings.test"
        )
