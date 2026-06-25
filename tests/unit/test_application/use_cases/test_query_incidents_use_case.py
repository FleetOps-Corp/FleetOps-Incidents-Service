"""Unit tests for QueryIncidentsUseCase."""

import pytest
from uuid import uuid4
from datetime import datetime

from incidents.application.dtos import QueryFiltersDTO
from incidents.application.exceptions import IncidentNotFoundApplicationError
from incidents.domain.models import Incident


class TestQueryIncidentsUseCase:
    """Test QueryIncidentsUseCase query functionality."""

    def test_execute_no_filters(
        self, query_incidents_use_case, mock_incident_repository
    ):
        """Given: No filters, When: Execute, Then: Return all incidents."""
        # Arrange
        incidents = [
            Incident.create(
                "c1",
                "ABC",
                "HUMANO",
                "GRAVE",
                "El conductor se enveneno",
                datetime.now(),
            ),
            Incident.create(
                "c2",
                "XYZ",
                "MECANICO",
                "LEVE",
                "El conductor se durmio",
                datetime.now(),
            ),
        ]
        mock_incident_repository.find_by_filters.return_value = incidents

        filters = QueryFiltersDTO()

        # Act
        result = query_incidents_use_case.execute(filters)

        # Assert
        assert len(result) == 2
        mock_incident_repository.find_by_filters.assert_called_once()

    def test_execute_with_tipo_filter(
        self, query_incidents_use_case, mock_incident_repository
    ):
        """Given: Type filter, When: Execute, Then: Return filtered incidents."""
        incident = Incident.create(
            "c1", "ABC", "MECANICO", "GRAVE", "El conductor se enveneno", datetime.now()
        )
        mock_incident_repository.find_by_filters.return_value = [incident]

        filters = QueryFiltersDTO(tipo_incidente="MECANICO")

        result = query_incidents_use_case.execute(filters)

        assert len(result) == 1
        assert str(result[0].tipo_incidente) == "MECANICO"

    def test_execute_by_id_found(
        self, query_incidents_use_case, mock_incident_repository
    ):
        """Given: Valid incident ID, When: Query, Then: Return incident."""
        incident_id = uuid4()
        incident = Incident.create(
            "c1", "ABC", "HUMANO", "GRAVE", "El conductor se enveneno", datetime.now()
        )
        incident.id = incident_id

        mock_incident_repository.find_by_id.return_value = incident

        result = query_incidents_use_case.execute_by_id(incident_id)

        assert result.id == str(incident_id)

    def test_execute_by_id_not_found(
        self, query_incidents_use_case, mock_incident_repository
    ):
        """Given: Invalid incident ID, When: Query, Then: Raise error."""
        incident_id = uuid4()
        mock_incident_repository.find_by_id.return_value = None

        with pytest.raises(IncidentNotFoundApplicationError):
            query_incidents_use_case.execute_by_id(incident_id)
