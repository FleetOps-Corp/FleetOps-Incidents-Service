"""REST API Views - Endpoint handlers for incident operations."""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.request import Request

from incidents.application.dtos import IncidentDTO, QueryFiltersDTO
from incidents.application.exceptions import (
    ApplicationException,
    VehicleValidationError,
)
from incidents.domain.exceptions import DomainException
from incidents.infrastructure.api.serializers import (
    IncidentRequestSerializer,
    IncidentResponseSerializer,
    IncidentQuerySerializer,
)
from incidents.infrastructure.adapters.logging import logger_factory

logger = logger_factory.LoggerFactory().get_logger(__name__)

register_incident_uc = None
query_incidents_uc = None


def set_use_cases(register_uc, query_uc):
    """Set use case instances (initialization)."""
    global register_incident_uc, query_incidents_uc
    register_incident_uc = register_uc
    query_incidents_uc = query_uc


# Permission classes need to be changed


@api_view(["POST"])
@permission_classes([AllowAny])
def create_incident(request: Request) -> Response:
    """
    POST /api/incidents/

    Register a new incident.

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
            raise RuntimeError("Use case not configured")

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
        logger.error(f"Application exception: {str(e)}")
        return Response(
            {"error": str(e), "code": e.code},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    except Exception as e:
        logger.error(f"Unexpected error in create_incident: {str(e)}")
        return Response(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([AllowAny])
def query_incidents(request: Request) -> Response:
    """
    GET /api/incidents/

    Query incidents with optional filters.

    Query parameters:
    - tipo_incidente: HUMANO or MECANICO
    - gravedad: LEVE or GRAVE
    - placa: Vehicle plate
    - id_conductor: Conductor ID
    - fecha_desde: Start date (ISO format)
    - fecha_hasta: End date (ISO format)

    Args:
        request: HTTP request with query parameters

    Returns:
        Response: HTTP 200 with incident list or error
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
        logger.error(f"Application exception: {str(e)}")
        return Response(
            {"error": str(e), "code": e.code},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    except Exception as e:
        logger.error(f"Unexpected error in query_incidents: {str(e)}")
        return Response(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([AllowAny])
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
            raise RuntimeError("Use case not configured")
        response_dto = query_incidents_uc.execute_by_id(incident_id)
        response_serializer = IncidentResponseSerializer(response_dto.to_dict())
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    except ValueError:
        return Response(
            {"error": "Invalid incident ID format"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    except Exception as e:
        logger.error(f"Error retrieving incident: {str(e)}")
        return Response(
            {"error": "Incident not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
