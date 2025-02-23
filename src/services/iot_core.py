import boto3

from src.constants import AWS_ENDPOINT, AWS_REGION
from src.logger import logger


class IotDataService:
    def __init__(self):
        self.client = boto3.client("iot-data", endpoint_url=AWS_ENDPOINT, region_name=AWS_REGION)

    def publish(self, topic: str, payload: str, **kwargs):
        try:
            self.client.publish(topic=topic, payload=payload, **kwargs)
            logger.info(f"Published a message to topic {topic} successfully")
        except Exception as e:
            logger.error(f"Fail to publish message<payload={payload:.40}> to topic {topic}: {e}")
