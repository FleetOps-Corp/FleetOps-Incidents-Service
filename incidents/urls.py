"""Root URL configuration."""

from django.http import JsonResponse
from django.urls import include, path


def health_check(request):
    return JsonResponse({"status": "ok", "service": "incidents"})


urlpatterns = [
    path("health", health_check, name="health_check"),
    path("api/", include("incidents.infrastructure.api.urls")),
]
