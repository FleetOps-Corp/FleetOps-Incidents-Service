"""Global error handler middleware."""

from rest_framework import status
from rest_framework.response import Response
from incidents.infrastructure.adapters.logging.logger_factory import logger_factory

logger = logger_factory.get_logger(__name__)


class ErrorHandlerMiddleware:
    """Middleware for global error handling."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            logger.error(f"Unhandled exception: {str(e)}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
