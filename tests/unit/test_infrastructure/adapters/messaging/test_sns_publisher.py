"""Unit tests for SNS publisher adapter."""

from unittest.mock import Mock, patch

import pytest

from incidents.infrastructure.adapters.messaging.sns_publisher import (
    SNSMessagePublisher,
)


class TestSNSMessagePublisher:
    """Test SNS publisher adapter."""

    @pytest.fixture
    def publisher(self):
        """Create publisher instance."""
        return SNSMessagePublisher(
            topic_arn="arn:aws:sns:us-east-1:255615880629:incidents_topic",
            region_name="us-east-1",
        )

    @patch("incidents.infrastructure.adapters.messaging.sns_publisher.boto3.client")
    def test_publish_success(self, mock_boto_client):
        """Given: Valid payload, When: Publish, Then: SNS publish called with correct args."""
        mock_sns = Mock()
        mock_boto_client.return_value = mock_sns

        publisher = SNSMessagePublisher(
            topic_arn="arn:aws:sns:us-east-1:255615880629:incidents_topic",
            region_name="us-east-1",
        )
        payload = {"id": "INC-123", "gravedad": "GRAVE"}

        publisher.publish(event_type="incident_registered", payload=payload)

        mock_sns.publish.assert_called_once()
        call_kwargs = mock_sns.publish.call_args.kwargs
        assert (
            call_kwargs["TopicArn"]
            == "arn:aws:sns:us-east-1:255615880629:incidents_topic"
        )
        assert "INC-123" in call_kwargs["Message"]
        assert (
            call_kwargs["MessageAttributes"]["event_type"]["StringValue"]
            == "incident_registered"
        )

    @patch("incidents.infrastructure.adapters.messaging.sns_publisher.boto3.client")
    def test_publish_failure_raises(self, mock_boto_client):
        """Given: SNS raises an error, When: Publish, Then: Exception propagates."""
        mock_sns = Mock()
        mock_sns.publish.side_effect = Exception("NoCredentialsError")
        mock_boto_client.return_value = mock_sns

        publisher = SNSMessagePublisher(
            topic_arn="arn:aws:sns:us-east-1:255615880629:incidents_topic",
            region_name="us-east-1",
        )

        with pytest.raises(Exception, match="NoCredentialsError"):
            publisher.publish(
                event_type="incident_registered", payload={"id": "INC-123"}
            )
