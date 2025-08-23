from typing import Iterable

import boto3
from types_boto3_lambda.client import LambdaClient
from types_boto3_lambda.type_defs import FunctionConfigurationTypeDef

from src.common.configs import AWS_ENDPOINT, AWS_REGION
from src.common.exceptions import InternalServerError
from src.common.meta import SingletonMeta


class FunctionConfiguration(FunctionConfigurationTypeDef):
    Tags: dict[str, str]


# Service -----------------------------------
class LambdaService(metaclass=SingletonMeta):
    client: LambdaClient

    def __init__(self):
        self.client = boto3.client("lambda", endpoint_url=AWS_ENDPOINT, region_name=AWS_REGION)

    def list_functions(self, **kwargs) -> Iterable[FunctionConfiguration]:
        try:
            response = self.client.list_functions(**kwargs)

            for function in response.get("Functions", []):
                tags = self.client.list_tags(Resource=function["FunctionArn"]).get("Tags", {})
                yield FunctionConfiguration(**function, Tags=tags)

            if cursor := response.get("NextMarker"):
                yield from self.list_functions(Marker=cursor)

        # except self.client.exceptions.ClientError as e:
        #     raise AWSClientException(f"[ClientException] Failed to list Lambda functions: {e}")

        except Exception as e:
            raise InternalServerError(f"An unexpected error occurred while listing Lambda functions: {e}")
