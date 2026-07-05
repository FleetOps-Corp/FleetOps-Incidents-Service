"""Django app configuration."""

from django.apps import AppConfig
from dotenv import load_dotenv

load_dotenv()


class IncidentsConfig(AppConfig):
    """Configuration for Incidents microservice Django app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "incidents"
    verbose_name = "Incidents Microservice - FleetOps Platform"

    def ready(self):

        from .container import configure_application

        configure_application()
