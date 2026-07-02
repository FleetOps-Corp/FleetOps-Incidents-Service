"""REST API URL Configuration."""

from django.urls import path

from incidents.infrastructure.api import views

app_name = "incidents_api"

urlpatterns = [
    # Incident creation and queries
    path("incidents/", views.query_incidents, name="query_incidents"),
    path("incidents/create/", views.create_incident, name="create_incident"),
    path("incidents/<str:incident_id>/", views.get_incident, name="get_incident"),
]
