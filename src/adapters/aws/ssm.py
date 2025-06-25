import boto3
from types_boto3_ssm.client import SSMClient

from src.common.meta import SingletonMeta


class SSMService(metaclass=SingletonMeta):
    client: SSMClient

    def __init__(self):
        self.client = boto3.client("ssm")
