from typing import Iterable

import boto3
from types_boto3_lambda.client import LambdaClient
from types_boto3_lambda.type_defs import FunctionConfigurationTypeDef

from src.common.constants import AWS_ENDPOINT, AWS_REGION
from src.common.exceptions import InternalServerError
from src.common.meta import SingletonMeta


# Service -----------------------------------
class LambdaService(metaclass=SingletonMeta):
    client: LambdaClient

    def __init__(self, region=AWS_REGION, endpoint_url=AWS_ENDPOINT):
        self.client = boto3.client("lambda", region_name=region, endpoint_url=endpoint_url)

    def list_functions_by_tag(self, tag_name: str, tag_value: str, **kwargs) -> Iterable[FunctionConfigurationTypeDef]:
        try:
            response = self.client.list_functions(**kwargs)

            for function in response.get("Functions", []):
                tags = self.client.list_tags(Resource=function["FunctionArn"]).get("Tags", {})
                if tags.get(tag_name, "") == tag_value:
                    yield function

            if cursor := response.get("NextMarker"):
                yield from self.list_functions(tag_name, tag_value, Marker=cursor)

        except Exception as e:
            raise InternalServerError(f"An unexpected error occurred while listing Lambda functions: {e}")
