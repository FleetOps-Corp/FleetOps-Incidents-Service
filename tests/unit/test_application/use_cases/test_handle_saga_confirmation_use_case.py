# """Unit tests for HandleSagaConfirmationUseCase.

# NOTE: This use case is kept for reference but is not actively used.
# The incident model no longer has state transitions (no EN_GESTION state),
# so SAGA confirmation handling is not required. Future enhancement if needed.
# """

# import pytest
# from uuid import uuid4

# from incidents.application.use_cases import HandleSagaConfirmationUseCase
# from incidents.application.exceptions import SagaOrchestrationError


# class TestHandleSagaConfirmationUseCase:
#     """Test SAGA coordination - Currently unused but kept for reference."""

#     def test_initialization(self, mock_incident_repository):
#         """Given: Service initialized, When: Create use case, Then: Success."""
#         use_case = HandleSagaConfirmationUseCase(
#             incident_service=type('obj', (object,), {})()
#         )
#         assert use_case is not None
