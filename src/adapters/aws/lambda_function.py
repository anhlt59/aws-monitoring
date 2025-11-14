from typing import AsyncIterable

import aioboto3
from types_aioboto3_lambda.client import LambdaClient
from types_boto3_lambda.type_defs import FunctionConfigurationTypeDef

from src.common.constants import AWS_ENDPOINT, AWS_REGION
from src.common.exceptions import InternalServerError
from src.common.meta import SingletonMeta


class FunctionConfiguration(FunctionConfigurationTypeDef):
    Tags: dict[str, str]


# Service -----------------------------------
class LambdaService(metaclass=SingletonMeta):
    def __init__(self, region=AWS_REGION, endpoint_url=AWS_ENDPOINT):
        self.region = region
        self.endpoint_url = endpoint_url
        self.session = aioboto3.Session()

    async def list_functions(self, **kwargs) -> AsyncIterable[FunctionConfiguration]:
        try:
            async with self.session.client("lambda", region_name=self.region, endpoint_url=self.endpoint_url) as client:
                response = await client.list_functions(**kwargs)

                for function in response.get("Functions", []):
                    tags_response = await client.list_tags(Resource=function["FunctionArn"])
                    tags = tags_response.get("Tags", {})
                    yield FunctionConfiguration(**function, Tags=tags)

                if cursor := response.get("NextMarker"):
                    async for func in self.list_functions(Marker=cursor):
                        yield func

        except Exception as e:
            raise InternalServerError(f"An unexpected error occurred while listing Lambda functions: {e}")
