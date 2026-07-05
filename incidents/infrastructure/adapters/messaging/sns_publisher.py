"""SNS Publisher Adapter - Publishes domain events to an SNS topic for fan-out
to multiple subscriber microservices via their own SQS queues."""

import json

import boto3

from incidents.domain.ports import MessagePublisherPort
from incidents.infrastructure.adapters.logging import logger_factory

logger = logger_factory.LoggerFactory().get_logger(__name__)


class SNSMessagePublisher(MessagePublisherPort):
    """
    Publishes events to an existing AWS SNS topic.

    Enables fan-out: multiple consumer microservices can each have their
    own SQS queue subscribed to this topic, and each receives an
    independent copy of every published event. This adapter only
    publishes; topic/subscription management is out of scope.

    Credentials are resolved automatically by boto3's default credential
    chain (IAM Role attached to the EC2 instance via Instance Profile).
    """

    def __init__(self, topic_arn: str, region_name: str):
        self.topic_arn = topic_arn
        self._client = boto3.client("sns", region_name=region_name)

    def publish(self, event_type: str, payload: dict) -> None:
        message_body = json.dumps(payload, default=str)

        try:
            self._client.publish(
                TopicArn=self.topic_arn,
                Message=message_body,
                MessageAttributes={
                    "event_type": {
                        "DataType": "String",
                        "StringValue": event_type,
                    }
                },
            )
        except Exception as e:
            logger.exception(f"Failed to publish event '{event_type}' to SNS: {str(e)}")
            raise
