"""SQS Publisher Adapter - Sends domain events to an existing AWS SQS queue."""

import json

import boto3

from incidents.domain.ports import MessagePublisherPort
from incidents.infrastructure.adapters.logging import logger_factory

logger = logger_factory.LoggerFactory().get_logger(__name__)


class SQSMessagePublisher(MessagePublisherPort):
    """
    Publishes events to an existing AWS SQS queue.

    This adapter only SENDS messages (SendMessage). It does not consume,
    create, or manage the queue's lifecycle.

    Credentials are resolved automatically by boto3's default credential
    chain (IAM Role attached to the EC2 instance via Instance Profile).
    No static access keys are used.
    """

    def __init__(self, queue_url: str, region_name: str):
        """
        Args:
            queue_url: Full URL of the existing SQS queue
            region_name: AWS region of the queue
        """
        self.queue_url = queue_url
        self._client = boto3.client("sqs", region_name=region_name)

    def publish(self, event_type: str, payload: dict) -> None:
        """
        Send a message to the SQS queue.

        Args:
            event_type: Logical event name, sent as a message attribute
            payload: Serializable event data

        Raises:
            Exception: Propagated if SQS SendMessage fails
        """
        message_body = json.dumps(payload, default=str)

        try:
            self._client.send_message(
                QueueUrl=self.queue_url,
                MessageBody=message_body,
                MessageAttributes={
                    "event_type": {
                        "DataType": "String",
                        "StringValue": event_type,
                    }
                },
            )
        except Exception as e:
            logger.exception(f"Failed to publish event '{event_type}' to SQS: {str(e)}")
            raise
