"""Unit tests for global error handler middleware."""

from incidents.infrastructure.api.middleware.error_handler import ErrorHandlerMiddleware


class TestErrorHandlerMiddleware:
    def test_returns_response_from_inner_handler(self):
        expected_response = object()

        middleware = ErrorHandlerMiddleware(lambda request: expected_response)

        result = middleware(object())

        assert result is expected_response

    def test_converts_unhandled_exception_to_response(self):
        middleware = ErrorHandlerMiddleware(
            lambda request: (_ for _ in ()).throw(Exception("boom"))
        )

        result = middleware(object())

        assert result.status_code == 500
        assert result.data == {"error": "Internal server error"}
