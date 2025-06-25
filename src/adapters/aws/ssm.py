import boto3
from types_boto3_ssm.client import SSMClient
from types_boto3_ssm.type_defs import ParameterTypeDef

from src.common.meta import SingletonMeta


class SSMService(metaclass=SingletonMeta):
    client: SSMClient

    def __init__(self):
        self.client = boto3.client("ssm")

    def get_parameter(self, key: str) -> ParameterTypeDef:
        response = self.client.get_parameter(Name=key, WithDecryption=True)
        return response["Parameter"]

    def create_parameter(self, key: str, value: str):
        self.client.put_parameter(Name=key, Value=value, Type="String", Overwrite=False)

    def put_parameter(self, key: str, value: str):
        self.client.put_parameter(Name=key, Value=value, Type="String", Overwrite=True)
