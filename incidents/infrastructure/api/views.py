"""REST API Views - Endpoint handlers for incident operations."""

import logging

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from incidents.application.dtos import IncidentDTO, QueryFiltersDTO
from incidents.application.exceptions import (
    ApplicationException,
    VehicleValidationError,
)
from incidents.domain.exceptions import DomainException
from incidents.infrastructure.adapters.logging import logger_factory
from incidents.infrastructure.api.permissions import HasIncidentAccess
from incidents.infrastructure.api.serializers import (
    IncidentQuerySerializer,
    IncidentRequestSerializer,
    IncidentResponseSerializer,
)

logger = logger_factory.LoggerFactory().get_logger(__name__)

register_incident_uc = None
query_incidents_uc = None

use_case_not_registered = "Use case not registered"


def set_use_cases(register_uc, query_uc):
    """Set use case instances (initialization)."""
    global register_incident_uc, query_incidents_uc
    register_incident_uc = register_uc
    query_incidents_uc = query_uc


# Permission classes need to be changed


@extend_schema(
    tags=["Incidents"],
    summary="Crear un incidente",
    request=IncidentRequestSerializer,
    responses={
        201: IncidentResponseSerializer,
        400: OpenApiResponse(description="Datos inválidos"),
        422: OpenApiResponse(description="El vehículo no está registrado"),
        500: OpenApiResponse(description="Error interno del servidor"),
    },
)
@api_view(["POST"])
@permission_classes(
    [
        IsAuthenticated,
        HasIncidentAccess,
    ]
)
def create_incident(request: Request) -> Response:
    """
    POST /api/incidents/

    Register a new incident.

    The request payload is validated and converted into an IncidentDTO.
    The corresponding application use case is executed to register the incident.

    Primary transactional flow exercising all architectural layers:
    1. API Gateway validates JWT token
    2. Django REST Framework deserializes request
    3. Application use case validates vehicle (Circuit Breaker)
    4. Domain service creates incident aggregate
    5. Repository persists to PostgreSQL
    6. Message broker publishes event for SAGA coordination
    7. Response returned to client

    Args:
        request: HTTP request with incident data

    Returns:
        Response: HTTP 201 with incident data or error

    """
    try:
        # Deserialize request
        serializer = IncidentRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Convert to DTO
        incident_dto = IncidentDTO(
            driver_id=serializer.validated_data["driver_id"],
            vehicle_id=serializer.validated_data["vehicle_id"],
            incident_type=serializer.validated_data["incident_type"],
            severity=serializer.validated_data["severity"],
            description=serializer.validated_data.get("description"),
            event_date=serializer.validated_data.get("event_date"),
        )

        # Execute use case
        if register_incident_uc is None:
            raise RuntimeError(use_case_not_registered)

        response_dto = register_incident_uc.execute(incident_dto)

        # Serialize response
        response_serializer = IncidentResponseSerializer(response_dto.to_dict())

        logger.info(f"Incident created: {response_dto.incident_id}")
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    except VehicleValidationError as e:
        logger.warning(f"Vehicle validation error: {str(e)}")
        return Response(
            {"error": str(e), "code": "VEHICLE_NOT_REGISTERED"},
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    except DomainException as e:
        logger.warning(f"Domain exception: {str(e)}")
        return Response(
            {"error": str(e), "code": e.code},
            status=status.HTTP_400_BAD_REQUEST,
        )

    except ApplicationException as e:
        logging.exception(f"Application exception: {str(e)}")
        return Response(
            {"error": str(e), "code": e.code},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    except Exception as e:
        logging.exception(f"Unexpected error in create_incident: {str(e)}")
        return Response(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@extend_schema(
    tags=["Incidents"],
    summary="Consultar incidentes",
    request=None,
    responses={
        200: IncidentResponseSerializer(many=True),
        400: OpenApiResponse(description="Filtros inválidos"),
        500: OpenApiResponse(description="Error interno del servidor"),
    },
)
@api_view(["GET"])
@permission_classes(
    [
        IsAuthenticated,
        HasIncidentAccess,
    ]
)
def query_incidents(request: Request) -> Response:
    """
    GET /api/incidents/

    Retrieve incidents using optional query filters.

    Query parameters:
    - incident_type: Type of incident.
    - severity: Incident severity.
    - vehicle_id: Vehicle identifier.
    - driver_id: Driver identifier.
    - start_date: Start date (ISO 8601 format).
    - end_date: End date (ISO 8601 format).

    Args:
        request: HTTP request containing optional query parameters.

    Returns:
        Response: HTTP 200 with a list of incidents or an error response.
    """
    try:
        # Deserialize query parameters
        serializer = IncidentQuerySerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Convert to DTO
        filters_dto = QueryFiltersDTO(
            incident_type=serializer.validated_data.get("incident_type"),
            severity=serializer.validated_data.get("severity"),
            vehicle_id=serializer.validated_data.get("vehicle_id"),
            driver_id=serializer.validated_data.get("driver_id"),
            start_date=serializer.validated_data.get("start_date"),
            end_date=serializer.validated_data.get("end_date"),
        )
        # Execute use case
        if query_incidents_uc is None:
            raise RuntimeError("Use case not configured")

        response_dtos = query_incidents_uc.execute(filters_dto)

        # Serialize responses
        response_data = [dto.to_dict() for dto in response_dtos]

        logger.info(f"Query executed: returned {len(response_data)} incidents")
        return Response(response_data, status=status.HTTP_200_OK)

    except ApplicationException as e:
        logging.exception(f"Application exception: {str(e)}")
        return Response(
            {"error": str(e), "code": e.code},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    except Exception as e:
        logging.exception(f"Unexpected error in query_incidents: {str(e)}")
        return Response(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@extend_schema(
    tags=["Incidents"],
    summary="Obtener un incidente por ID",
    request=None,
    responses={
        200: IncidentResponseSerializer,
        400: OpenApiResponse(description="Formato de ID inválido"),
        404: OpenApiResponse(description="Incidente no encontrado"),
    },
)
@api_view(["GET"])
@permission_classes(
    [
        IsAuthenticated,
        HasIncidentAccess,
    ]
)
def get_incident(request: Request, incident_id: str) -> Response:
    """
    GET /api/incidents/{incident_id}/

    Retrieve a single incident by ID.

    Args:
        request: HTTP request
        incident_id: UUID of incident

    Returns:
        Response: HTTP 200 with incident data or 404
    """
    try:
        if query_incidents_uc is None:
            raise RuntimeError(use_case_not_registered)
        response_dto = query_incidents_uc.execute_by_id(incident_id)
        response_serializer = IncidentResponseSerializer(response_dto.to_dict())
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    except ValueError:
        return Response(
            {"error": "Invalid incident ID format"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    except Exception as e:
        logging.exception(f"Error retrieving incident: {str(e)}")
        return Response(
            {"error": "Incident not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
