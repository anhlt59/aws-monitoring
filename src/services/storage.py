import boto3

from src.constants import AWS_ENDPOINT, AWS_REGION, S3_BUCKET_NAME


class StorageService:
    def __init__(self):
        self.client = boto3.client("s3", endpoint_url=AWS_ENDPOINT, region_name=AWS_REGION)

    def get_object(self, key: str, bucket: str = S3_BUCKET_NAME) -> str:
        """
        Get an object from S3 bucket using the provided key.
        Args:
            key    (str): The key (path) of the object in S3
            bucket (str): The bucket name
        Returns:
            str: The content of the object
        """
        response = self.client.get_object(Bucket=bucket, Key=key)
        return response.get("Body").read().decode("utf-8")
