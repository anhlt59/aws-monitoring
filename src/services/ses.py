import boto3

from src.constants import AWS_ENDPOINT, AWS_REGION, SES_SENDER_NAME
from src.logger import logger
from src.types import SesEmailItem


class SesService:
    def __init__(self):
        self.client = boto3.client("ses", endpoint_url=AWS_ENDPOINT, region_name=AWS_REGION)

    def send_emails(self, email: SesEmailItem):
        response = self.client.send_email(
            Source=SES_SENDER_NAME,
            Destination={"ToAddresses": email.recipients},
            Message={"Subject": {"Data": email.subject}, "Body": {"Text": {"Data": email.message}}},
        )
        logger.info(f"Sent {email} successfully: {response.get('MessageId')}")
